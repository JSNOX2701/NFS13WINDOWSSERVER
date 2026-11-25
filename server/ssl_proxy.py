# Copyright (C) 2026 sn0wd0wn / Windows port
# SPDX-License-Identifier: AGPL-3.0-only
"""
Native SSLv3 terminating frontend for Need for Speed: Most Wanted (2012) on Windows.
Replaces the Linux stunnel-ssl3 Docker container using pure-Python tlslite-ng.

Accepts:
- TCP 42127: Blaze RPC (SSLv3) -> forwards to 127.0.0.1:42128 with HAProxy PROXY v1 header
- TCP 44125: HTTPS Redirector (SSLv3) -> forwards to 127.0.0.1:44126
"""

import os
import sys
import socket
import logging
import threading
from pathlib import Path

try:
    from tlslite.api import TLSConnection, X509CertChain, X509, parsePEMKey, HandshakeSettings
except ImportError:
    print("[ERROR] 'tlslite-ng' is required for the Windows SSLv3 frontend.", file=sys.stderr)
    print("Please install it by running: pip install tlslite-ng", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SSL3-FRONTEND] %(message)s")
log = logging.getLogger("ssl_proxy")

# Default ports
BLAZE_SSL_PORT = 42127
BLAZE_BACKEND_PORT = 42128

HTTPS_SSL_PORT = 44125
HTTPS_BACKEND_PORT = 44126

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CERT = REPO_ROOT / "certs" / "cert.pem"
DEFAULT_KEY = REPO_ROOT / "certs" / "key.pem"


def load_credentials(cert_path=DEFAULT_CERT, key_path=DEFAULT_KEY):
    if not cert_path.exists() or not key_path.exists():
        raise FileNotFoundError(
            f"Certificate ({cert_path}) or Key ({key_path}) not found.\n"
            f"Please generate them first."
        )
    x509 = X509()
    x509.parse(cert_path.read_text(encoding="ascii", errors="ignore"))
    cert_chain = X509CertChain([x509])
    key = parsePEMKey(key_path.read_text(encoding="ascii", errors="ignore"), private=True)
    return cert_chain, key


def forward_stream(src_reader, dst_writer, stop_event):
    while not stop_event.is_set():
        try:
            data = src_reader()
            if not data:
                break
            dst_writer(data)
        except Exception:
            break
    stop_event.set()


def handle_client_connection(client_sock, client_addr, backend_port, cert_chain, key, use_proxy_protocol=True):
    client_ip, client_port = client_addr[0], client_addr[1]
    backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tls_conn = None
    stop_event = threading.Event()

    try:
        tls_conn = TLSConnection(client_sock)
        settings = HandshakeSettings()
        # Restrict strictly to SSLv3 / TLS 1.0 compatibility for EA DirtySock
        settings.minVersion = (3, 0)
        settings.maxVersion = (3, 1)

        tls_conn.handshakeServer(certChain=cert_chain, privateKey=key, settings=settings)
        ver_str = f"{tls_conn.version[0]}.{tls_conn.version[1]}"
        log.info(f"Handshake success from {client_ip}:{client_port} (SSL version {ver_str})")

        backend_sock.connect(("127.0.0.1", backend_port))

        if use_proxy_protocol:
            # Send HAProxy PROXY v1 line so server.py knows the player's true LAN IP
            proxy_line = f"PROXY TCP4 {client_ip} 127.0.0.1 {client_port} {BLAZE_SSL_PORT}\r\n".encode("ascii")
            backend_sock.sendall(proxy_line)

        def close_all():
            stop_event.set()
            try:
                if tls_conn:
                    tls_conn.close()
            except Exception:
                pass
            try:
                client_sock.close()
            except Exception:
                pass
            try:
                backend_sock.close()
            except Exception:
                pass

        t_in = threading.Thread(
            target=forward_stream,
            args=(lambda: tls_conn.read(4096), backend_sock.sendall, stop_event),
            daemon=True
        )
        t_out = threading.Thread(
            target=forward_stream,
            args=(lambda: backend_sock.recv(4096), tls_conn.write, stop_event),
            daemon=True
        )

        t_in.start()
        t_out.start()

        # Wait until either side disconnects
        stop_event.wait()
        close_all()

    except (EOFError, ConnectionResetError, BrokenPipeError, OSError) as exc:
        log.debug(f"Connection closed during SSL handshake/relay from {client_ip}:{client_port}: {exc}")
    except TypeError as exc:
        # tlslite-ng raises TypeError("'NoneType' object is not iterable") when a
        # client opens and immediately closes a probe socket before ClientHello.
        if "NoneType" in str(exc):
            log.debug(f"Empty TCP probe closed early from {client_ip}:{client_port}")
        else:
            log.warning(f"Error handling connection from {client_ip}:{client_port} -> backend :{backend_port}: {exc}")
    except Exception as exc:
        log.warning(f"Error handling connection from {client_ip}:{client_port} -> backend :{backend_port}: {exc}")
    finally:
        stop_event.set()
        try:
            client_sock.close()
        except Exception:
            pass
        try:
            backend_sock.close()
        except Exception:
            pass
        log.info(f"Closed connection from {client_ip}:{client_port}")


def run_listener(listen_port, backend_port, cert_chain, key, use_proxy_protocol=True):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", listen_port))
    server_sock.listen(64)
    service_name = "Blaze (SSLv3)" if use_proxy_protocol else "HTTPS (SSLv3)"
    log.info(f"Listening on 0.0.0.0:{listen_port} [{service_name}] -> 127.0.0.1:{backend_port}")

    while True:
        try:
            client_sock, client_addr = server_sock.accept()
            th = threading.Thread(
                target=handle_client_connection,
                args=(client_sock, client_addr, backend_port, cert_chain, key, use_proxy_protocol),
                daemon=True
            )
            th.start()
        except Exception as exc:
            log.error(f"Listener on port {listen_port} encountered error: {exc}")


def start_frontend_threads(cert_path=DEFAULT_CERT, key_path=DEFAULT_KEY):
    cert_chain, key = load_credentials(cert_path, key_path)

    t_blaze = threading.Thread(
        target=run_listener,
        args=(BLAZE_SSL_PORT, BLAZE_BACKEND_PORT, cert_chain, key, True),
        daemon=True
    )
    t_https = threading.Thread(
        target=run_listener,
        args=(HTTPS_SSL_PORT, HTTPS_BACKEND_PORT, cert_chain, key, False),
        daemon=True
    )

    t_blaze.start()
    t_https.start()
    return t_blaze, t_https


if __name__ == "__main__":
    log.info("Starting standalone SSLv3 frontend for Windows...")
    cert_chain, key = load_credentials()
    t1, t2 = start_frontend_threads()
    log.info("SSLv3 frontend running. Press Ctrl+C to stop.")
    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        log.info("Stopping SSLv3 frontend.")
