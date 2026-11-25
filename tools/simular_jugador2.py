#!/usr/bin/env python3
"""
Simulador de Segundo Jugador ("GhostRival") para Need for Speed: Most Wanted (2012)
Permite probar en una sola PC (sin necesitar a otra persona conectada):
  1. El flujo completo de login SSLv3 + Blaze desde una segunda IP local (127.0.0.2).
  2. El anuncio en vivo de presencia de amigos (AssociationLists + UserSessions SUBS=1 + lookupUser),
     que era exactamente donde antes crasheaba el primer jugador en 0x00A82B55.
  3. Descubrimiento automático de tu sesión activa (Friends Game o Public Matchmaking) y unión
     como segundo jugador (NotifyPlayerJoining + updateMeshConnection).

Uso:
  1. Abre tu juego normalmente con HOST AND PLAY y entra al modo Multijugador / crea sesión.
  2. Ejecuta `tools\\simular_jugador2.bat` (o `python tools\\simular_jugador2.py`).
  3. Presiona Ctrl+C cuando termines de probar; el bot saldrá limpiamente de la sesión.
"""

import argparse
import ipaddress
import json
import socket
import struct
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "server"))

from tlslite.api import HandshakeSettings, TLSConnection  # noqa: E402
import server as blaze  # noqa: E402


class BoundHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, source_ip: str):
        super().__init__()
        self._source_ip = source_ip

    def http_open(self, req):
        return self.do_open(
            lambda host, **kw: urllib.request.http.client.HTTPConnection(
                host, source_address=(self._source_ip, 0), **kw
            ),
            req,
        )


class GhostBlazeClient:
    def __init__(self, host_ip="127.0.0.1", port=42127, source_ip="127.0.0.2", name="GhostRival"):
        self.host_ip = host_ip
        self.port = port
        self.source_ip = source_ip
        self.name = name
        self.sock = None
        self.tls = None
        self.msg_id = 1
        self.persona_id = 0
        self.joined_gid = 0
        self._rx_buf = bytearray()
        self._rx_cond = threading.Condition()
        self._rx_eof = False

    def connect(self):
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw.settimeout(5.0)
        raw.bind((self.source_ip, 0))
        raw.connect((self.host_ip, self.port))
        tls = TLSConnection(raw)
        settings = HandshakeSettings()
        settings.minVersion = (3, 0)
        settings.maxVersion = (3, 1)
        tls.handshakeClientCert(settings=settings)
        raw.settimeout(None)
        self.sock = raw
        self.tls = tls
        threading.Thread(target=self._rx_worker, daemon=True).start()
        print(f"[+] Conectado por SSLv3 ({tls.version[0]}.{tls.version[1]}) desde {self.source_ip} -> {self.host_ip}:{self.port}")

    def _rx_worker(self):
        try:
            while True:
                chunk = self.tls.read(4096)
                if not chunk:
                    break
                with self._rx_cond:
                    self._rx_buf.extend(chunk)
                    self._rx_cond.notify_all()
        except Exception:
            pass
        finally:
            with self._rx_cond:
                self._rx_eof = True
                self._rx_cond.notify_all()

    def _read_exact(self, n: int, timeout: float = 5.0) -> bytes | None:
        deadline = time.time() + timeout
        with self._rx_cond:
            while len(self._rx_buf) < n:
                if self._rx_eof:
                    raise EOFError("El servidor cerró la conexión SSL.")
                rem = deadline - time.time()
                if rem <= 0:
                    return None
                self._rx_cond.wait(timeout=rem)
            out = bytes(self._rx_buf[:n])
            del self._rx_buf[:n]
            return out

    def recv_frame(self, timeout: float = 2.0):
        hdr = self._read_exact(12, timeout=timeout)
        if hdr is None:
            return None
        length, comp, cmd, err, qtype, mid = struct.unpack(">6H", hdr)
        payload = self._read_exact(length, timeout=5.0) if length else b""
        if payload is None:
            raise EOFError("Payload Blaze truncado.")
        return comp, cmd, err, qtype, mid, payload

    def send_rpc(self, component: int, command: int, payload: bytes = b""):
        mid = self.msg_id
        self.msg_id += 1
        hdr = struct.pack(">6H", len(payload), component, command, 0, 0x0000, mid)
        self.tls.write(hdr + payload)
        while True:
            frame = self.recv_frame(timeout=5.0)
            if frame is None:
                raise TimeoutError(f"Timeout esperando respuesta RPC 0x{component:04X}:0x{command:04X}")
            comp, cmd, err, qtype, rmid, body = frame
            if qtype in (0x1000, 0x3000) and rmid == mid:
                return err, body
            self._log_notification(comp, cmd, body)

    def drain_notifications(self, duration: float = 0.25):
        deadline = time.time() + duration
        while time.time() < deadline:
            rem = max(0.05, deadline - time.time())
            frame = self.recv_frame(timeout=rem)
            if frame is None:
                break
            comp, cmd, _, qtype, _, body = frame
            if qtype == 0x2000:
                self._log_notification(comp, cmd, body)

    def _log_notification(self, comp: int, cmd: int, body: bytes):
        if comp == 0x7802 and cmd == 0x0008:
            self.persona_id = blaze.find_tdf_int(body, "BUID", 0)
            dsnm = blaze.find_tdf_string(body, "DSNM", "")
            print(f"    [Notif] UserAuthenticated -> {dsnm} (ID={self.persona_id})")
        elif comp == 0x7802 and cmd == 0x0002:
            user = blaze.find_tdf_field(body, "USER", 0x03)
            uname = blaze.find_tdf_string(user[4:-1], "NAME", "?") if user else "?"
            uid = blaze.find_tdf_int(user[4:-1], "ID", 0) if user else 0
            print(f"    [Notif] NotifyUserAdded -> {uname} (ID={uid})")
        elif comp == 0x7802 and cmd == 0x0001:
            uid = blaze.find_tdf_int(body, "USID", 0)
            subs = blaze.find_tdf_int(body, "SUBS", 0)
            print(f"    [Notif] ExtendedDataUpdate -> USID={uid} SUBS={subs}")
        elif comp == 0x0004 and cmd == 0x0014:
            game = blaze.find_tdf_field(body, "GAME", 0x03)
            gid = blaze.find_tdf_int(game[4:-1], "GID", 0) if game else 0
            gnam = blaze.find_tdf_string(game[4:-1], "GNAM", "?") if game else "?"
            print(f"    [Notif] NotifyGameSetup -> GID={gid} ({gnam})")
            self.joined_gid = gid
        else:
            print(f"    [Notif] Comp=0x{comp:04X} Cmd=0x{cmd:04X} ({len(body)} bytes)")

    def build_network_info_request(self) -> bytes:
        ip_int = int(ipaddress.IPv4Address("127.0.0.2"))
        addr = blaze._fallback_network_address("ADDR", ip=ip_int, port=3660)
        nqos = (
            blaze.encode_tag("NQOS", 0x03) +
            blaze.tdf_int_field("DBPS", 0) +
            blaze.tdf_int_field("NATT", 1) +
            blaze.tdf_int_field("UBPS", 0) +
            b"\x00"
        )
        return addr + nqos

    def login_and_announce(self):
        print("[1/4] Ejecutando preAuth + expressLogin...")
        self.send_rpc(0x0009, 0x0007, b"")
        self.send_rpc(0x0001, 0x003C, b"")
        self.drain_notifications(0.20)

        # Renombrar perfil en vivo por HTTP desde 127.0.0.2
        try:
            opener = urllib.request.build_opener(BoundHTTPHandler(self.source_ip))
            with opener.open(f"http://127.0.0.1:8080/rename?name={self.name}", timeout=2.0) as resp:
                resp.read()
        except Exception:
            pass

        print("[2/4] Ejecutando postAuth (dispara NotifyUserAdded + NotifyUpdateListWithMembers a tu juego)...")
        self.send_rpc(0x0009, 0x0008, b"")
        self.drain_notifications(0.25)

        print("[3/4] Publicando info de red (ADDR/QDAT) y consultando friendList + lookupUser...")
        self.send_rpc(0x7802, 0x0014, self.build_network_info_request())
        self.drain_notifications(0.15)

        alst_req = (
            blaze.encode_tag("ALST", 0x04) + b"\x03\x01" +
            blaze.encode_tag("LID", 0x03) +
            blaze.tdf_int_field("TYPE", 1) + b"\x00\x00\x00"
        )
        _, lists_resp = self.send_rpc(0x0019, 0x0006, alst_req)
        self.drain_notifications(0.15)

        # Probar lookupUser (0x7802, 0x000C) igual que hace el ejecutable real
        if self.persona_id != 1000001:
            err, udata = self.send_rpc(0x7802, 0x000C, blaze.tdf_int_field("ID", 1000001) + b"\x00")
            if err == 0 and udata:
                ugrp = blaze.find_tdf_field(udata, "USER", 0x03)
                host_name = blaze.find_tdf_string(ugrp[4:-1], "NAME", "Host") if ugrp else "Host"
                print(f"    [OK] lookupUser(1000001) respondió correctamente -> {host_name} ({len(udata)} bytes)")

    def discover_and_join_game(self, wait_seconds: int = 60) -> bool:
        print(f"[4/4] Buscando partida activa en el servidor (esperando hasta {wait_seconds}s)...")
        deadline = time.time() + wait_seconds
        ip_int = int(ipaddress.IPv4Address("127.0.0.2"))
        pnet = blaze._fallback_network_address("PNET", ip=ip_int, port=3660)

        while time.time() < deadline:
            _, lg_resp = self.send_rpc(0x0004, 0x0011, b"")
            games = blaze.find_tdf_group_list(lg_resp, "LGAM")
            if games:
                g_field = blaze.find_tdf_field(games[0], "GAME", 0x03)
                gid = blaze.find_tdf_int(g_field[4:-1], "GID", 0) if g_field else 0
                gnam = blaze.find_tdf_string(g_field[4:-1], "GNAM", "Session") if g_field else "Session"
                vstr = blaze.find_tdf_string(g_field[4:-1], "VSTR", "nfs-2013-pc") if g_field else "nfs-2013-pc"
                if gid > 0:
                    print(f"[+] ¡Partida encontrada! GID={gid} ('{gnam}', ver={vstr}). Uniéndose como Jugador 2...")
                    join_req = (
                        blaze.tdf_int_field("GID", gid) +
                        blaze.tdf_string_field("GVER", vstr) +
                        pnet +
                        blaze.tdf_int_field("SLOT", 0) +
                        b"\x00"
                    )
                    err, _ = self.send_rpc(0x0004, 0x0009, join_req)
                    self.drain_notifications(0.40)
                    if err == 0:
                        self.joined_gid = gid
                        # Completar estado de malla (updateMeshConnection -> state=4 + PlayerJoinCompleted)
                        targ = (
                            blaze.encode_tag("TARG", 0x04) + b"\x03\x01" +
                            blaze.tdf_int_field("PID", self.persona_id) +
                            blaze.tdf_int_field("STAT", 2) + b"\x00"
                        )
                        self.send_rpc(0x0004, 0x001D, blaze.tdf_int_field("GID", gid) + targ + b"\x00")
                        self.drain_notifications(0.30)
                        print(f"[EXITO] {self.name} (ID={self.persona_id}) está DENTRO de la sesión GID={gid}!")
                        print("        Verifica en tu juego que NO hubo crash y que apareció la notificación del jugador.")
                        return True
            time.sleep(2.0)
            self.drain_notifications(0.10)
        print("[!] No se detectó ninguna partida creada todavía (pero el test de login/presencia de amigos ya pasó).")
        return False

    def keep_alive_loop(self, hold_seconds: float | None = None):
        print("\n[*] Manteniendo Jugador 2 conectado (Presiona Ctrl+C para desconectarlo limpiamente)...")
        start = time.time()
        last_ping = time.time()
        try:
            while True:
                if hold_seconds is not None and (time.time() - start) >= hold_seconds:
                    break
                self.drain_notifications(1.0)
                if time.time() - last_ping >= 12.0:
                    self.send_rpc(0x0009, 0x0002, b"")
                    last_ping = time.time()
        except KeyboardInterrupt:
            print("\n[*] Desconectando Jugador 2...")

    def close(self, clean_registry: bool = True):
        try:
            if self.tls and self.joined_gid:
                req = (
                    blaze.tdf_int_field("GID", self.joined_gid) +
                    blaze.tdf_int_field("PID", self.persona_id) +
                    blaze.tdf_int_field("REAS", 6) + b"\x00"
                )
                self.send_rpc(0x0004, 0x000B, req)
            if self.tls:
                self.send_rpc(0x0001, 0x0046, b"")
        except Exception:
            pass
        for obj in (self.tls, self.sock):
            try:
                if obj:
                    obj.close()
            except Exception:
                pass
        if clean_registry:
            pjson = ROOT_DIR / "server" / "players.json"
            if pjson.exists():
                try:
                    data = json.loads(pjson.read_text(encoding="utf-8"))
                    if "players" in data:
                        data["players"] = [
                            p for p in data["players"]
                            if p.get("client_ip") != self.source_ip
                        ]
                        pjson.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                except Exception:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Simula un 2do jugador Blaze uniéndose a tu partida.")
    parser.add_argument("--host", default="127.0.0.1", help="IP del servidor (default: 127.0.0.1)")
    parser.add_argument("--source-ip", default="127.0.0.2", help="IP origen simulada (default: 127.0.0.2)")
    parser.add_argument("--name", default="GhostRival", help="Nombre del jugador simulado")
    parser.add_argument("--wait", type=int, default=60, help="Segundos buscando partida activa")
    parser.add_argument("--hold", type=float, default=None, help="Segundos antes de salir automáticamente")
    args = parser.parse_args()

    bot = GhostBlazeClient(host_ip=args.host, source_ip=args.source_ip, name=args.name)
    try:
        bot.connect()
        bot.login_and_announce()
        bot.discover_and_join_game(wait_seconds=args.wait)
        bot.keep_alive_loop(hold_seconds=args.hold)
    finally:
        bot.close(clean_registry=True)
        print("[+] Jugador 2 desconectado limpiamente.")


if __name__ == "__main__":
    main()
