# Copyright (C) 2026 sn0wd0wn / Windows port
# SPDX-License-Identifier: AGPL-3.0-only
"""
All-in-one Windows Launcher for Need for Speed: Most Wanted (2012) Server.
Runs both the SSLv3 proxy and the Blaze/Autolog backend natively in a single process.
"""

import os
import sys
import socket
import asyncio
import logging
from pathlib import Path

# Add project root to sys.path
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent
    BASE_DIR = RESOURCE_DIR

sys.path.insert(0, str(RESOURCE_DIR))
sys.path.insert(0, str(RESOURCE_DIR / "server"))
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "server"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("nfs13-windows")


def get_default_lan_ip():
    """Detect local LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connecting to public DNS dummy address to discover default interface IP
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"
    finally:
        s.close()


def print_banner(host_ip):
    banner = f"""
================================================================================
   NEED FOR SPEED: MOST WANTED (2012) - SERVIDOR PRIVADO PARA WINDOWS
   (Basado en nfs13 sn0wd0wn - Adaptado 100% Nativo para Windows)
================================================================================

 [!] Servidor configurado en IP: {host_ip}
 
 [>] Servicios activos:
     * Blaze RPC (SSLv3)     : Puerto TCP 42127 -> backend :42128
     * HTTPS Redirect (SSLv3): Puerto TCP 44125 -> backend :44126
     * Autolog HTTP API      : Puerto TCP 8080 (http://{host_ip}:8080)
     * QoS Ping/Latency      : Puerto TCP/UDP 17500
     * Tráfico Carreras P2P  : Puerto UDP 3659 (Directo entre jugadores en LAN/VPN)

 [>] ¿Cómo elegir tu nombre de jugador?
     Abre tu navegador web o usa curl e ingresa:
     http://{host_ip}:8080/rename?name=TuNombre

 [>] Configuración del archivo HOSTS (C:\\Windows\\System32\\drivers\\etc\\hosts):
     Agrega las siguientes líneas en cada PC que vaya a jugar:
--------------------------------------------------------------------------------
{host_ip} gosredirector.ea.com
{host_ip} gosredirector.online.ea.com
{host_ip} gosredirector.scert.ea.com
{host_ip} gosredirector.stest.ea.com
{host_ip} gosca.ea.com
{host_ip} nfs13-pc.blaze.ea.com
{host_ip} demangler.ea.com
{host_ip} peach.online.ea.com
--------------------------------------------------------------------------------
 Presiona Ctrl + C en cualquier momento para detener el servidor.
================================================================================
"""
    print(banner)


def cleanup_zombie_instances(ports=(42127, 42128, 44125, 44126, 8080, 17500)):
    """Automatically frees ports if an old zombie python instance was left running."""
    import subprocess
    current_pid = os.getpid()
    cleaned = set()
    try:
        output = subprocess.check_output('netstat -ano -p tcp', shell=True).decode(errors='ignore')
        for line in output.splitlines():
            for port in ports:
                if f":{port} " in line:
                    parts = line.strip().split()
                    if parts:
                        try:
                            pid = int(parts[-1])
                            if pid != current_pid and pid > 0 and pid not in cleaned:
                                proc_check = subprocess.check_output(
                                    f'tasklist /FI "PID eq {pid}" /NH', shell=True
                                ).decode(errors='ignore')
                                if "python" in proc_check.lower():
                                    log.info(f"Liberando puerto {port} ocupado por instancia previa (PID {pid})...")
                                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                                    cleaned.add(pid)
                        except (ValueError, subprocess.SubprocessError):
                            pass
    except Exception as exc:
        log.debug(f"Error verificando instancias previas: {exc}")


def main():
    # Automatically clean up any hanging python process on our ports
    cleanup_zombie_instances()

    # Determine Host IP
    if len(sys.argv) > 1 and sys.argv[1].strip():
        host_ip = sys.argv[1].strip()
    elif os.environ.get("NFS13_HOST"):
        host_ip = os.environ.get("NFS13_HOST")
    else:
        host_ip = get_default_lan_ip()

    os.environ["NFS13_HOST"] = host_ip

    cert_path = RESOURCE_DIR / "certs" / "cert.pem"
    if not cert_path.exists():
        cert_path = BASE_DIR / "certs" / "cert.pem"

    key_path = RESOURCE_DIR / "certs" / "key.pem"
    if not key_path.exists():
        key_path = BASE_DIR / "certs" / "key.pem"

    if not cert_path.exists() or not key_path.exists():
        log.error(f"Certificados no encontrados en {cert_path.parent}. Por favor verifica la carpeta certs/")
        sys.exit(1)

    print_banner(host_ip)

    # Import SSLv3 frontend
    try:
        from server.ssl_proxy import start_frontend_threads
    except ImportError:
        from ssl_proxy import start_frontend_threads
    log.info("Iniciando proxy SSLv3 (DirtySock compatible) en puertos 42127 y 44125...")
    start_frontend_threads(cert_path=cert_path, key_path=key_path)

    # Import server backend
    import server as nfs_server
    # Update server module's host IP
    nfs_server.SERVER_HOST = host_ip
    nfs_server.AUTOLOG_URL = f"http://{host_ip}:8080"

    try:
        current_pool = nfs_server.get_current_event_pool()
        mode_str = os.environ.get("NFS13_SPEEDLIST_MODE", "all_races")
        log.info(f"Modo de Speedlist activo: [{mode_str}] con {len(current_pool)} carreras/eventos disponibles.")
    except Exception:
        pass

    log.info("Iniciando servicios backend (Blaze, Autolog, QoS)...")
    try:
        asyncio.run(nfs_server.main())
    except KeyboardInterrupt:
        print("\n[+] Servidor detenido de forma segura.")


if __name__ == "__main__":
    main()
