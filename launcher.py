#!/usr/bin/env python3
# Copyright (C) 2026 - NFS Most Wanted 2012 Private Launcher
# SPDX-License-Identifier: MIT
"""
Need for Speed: Most Wanted (2012) — Private Server Launcher
Criterion Games Aesthetic (White, Crimson Red, Slate Black).
Full config persistence, multi-language (5+ languages), live renaming, Radmin/LAN auto-detection.
"""

import os
import sys
import json
import socket
import shutil
import ctypes
import urllib.parse
import urllib.request
import urllib.error
import subprocess
import threading
import configparser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ─────────────────────────── Base & Resource Paths ───────────────────────────
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent
    BASE_DIR = RESOURCE_DIR

SERVER_SCRIPT  = BASE_DIR / "run_server.py"
if not SERVER_SCRIPT.exists():
    SERVER_SCRIPT = RESOURCE_DIR / "run_server.py"
if not SERVER_SCRIPT.exists():
    SERVER_SCRIPT = BASE_DIR / "run_server_windows.py"

SERVER_BAT     = BASE_DIR / "tools" / "iniciar_servidor.bat"
if not SERVER_BAT.exists():
    SERVER_BAT = BASE_DIR / "iniciar_servidor.bat"

PATCHER_SCRIPT = RESOURCE_DIR / "client" / "patch_nfs13.py"
if not PATCHER_SCRIPT.exists():
    PATCHER_SCRIPT = BASE_DIR / "client" / "patch_nfs13.py"

LAUNCHER_INI   = BASE_DIR / "launcher.ini"
PLAYERS_JSON   = BASE_DIR / "server" / "players.json"
HOSTS_FILE     = Path(r"C:\Windows\System32\drivers\etc\hosts")

ICON_FILE      = RESOURCE_DIR / "icon.ico"
if not ICON_FILE.exists():
    ICON_FILE = BASE_DIR / "icon.ico"
if not ICON_FILE.exists():
    ICON_FILE = BASE_DIR / "assets" / "icon.ico"

EA_DOMAINS = [
    "gosredirector.ea.com",
    "gosredirector.online.ea.com",
    "gosredirector.scert.ea.com",
    "gosredirector.stest.ea.com",
    "gosca.ea.com",
    "nfs13-pc.blaze.ea.com",
    "demangler.ea.com",
    "peach.online.ea.com",
]

HOSTS_TAG = "# NFSMW12 Private Server"

# ─────────────────────────── Color Palette (Criterion Red & White) ───────────
RED_PRIMARY   = "#D4001F"       # Criterion Most Wanted Racing Red
RED_HOVER     = "#B3001A"       # Darker red on hover
RED_ACCENT    = "#FF2438"       # Bright neon red
RED_TINT      = "#FFF0F2"       # Soft red background for callouts
RED_BORDER    = "#FFCCD3"       # Soft red border

BG_MAIN       = "#F5F6F9"       # Crisp clean off-white background
BG_WHITE      = "#FFFFFF"       # Pure white for cards/panels
BG_INPUT      = "#FFFFFF"       # Input field background
BORDER_LIGHT  = "#E1E4EA"       # Subtle border
BORDER_FOCUS  = "#D4001F"       # Focused border

TEXT_DARK     = "#0A0E17"       # Intense charcoal black for high contrast
TEXT_BODY     = "#333D4E"       # Crisp slate body text
TEXT_MUTED    = "#687385"       # Subtitles and hints
TEXT_WHITE    = "#FFFFFF"

GREEN_SUCCESS = "#059669"
GREEN_BG      = "#ECFDF5"
GREEN_BORDER  = "#A7F3D0"

# ─────────────────────────── Multi-Language Dictionaries ─────────────────────

LANGUAGES = {
    "es": "🇪🇸 Español",
    "en": "🇺🇸 English",
    "ru": "🇷🇺 Русский",
    "pt": "🇧🇷 Português",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
}

SPEEDLIST_MODES = {
    "all_races": {
        "es": "🏎️ Todas las Carreras (Sprints + Circuitos + DLC) [40 Trazados]",
        "en": "🏎️ All Races (Sprints + Circuits + Airport DLC) [40 Tracks]",
        "ru": "🏎️ Все гонки (Спринты + Кольцо + DLC Аэропорт) [40 трасс]",
        "pt": "🏎️ Todas as Corridas (Sprints + Circuitos + DLC Aeroporto) [40 Pistas]",
        "fr": "🏎️ Toutes les Courses (Sprints + Circuits + DLC Aéroport) [40 Circuits]",
        "de": "🏎️ Alle Rennen (Sprints + Rundkurse + Flughafen-DLC) [40 Strecken]",
    },
    "sprints": {
        "es": "⚡ Solo Sprints Punto a Punto [10 Trazados]",
        "en": "⚡ Point-to-Point Sprints Only [10 Base Tracks]",
        "ru": "⚡ Только спринты из точки в точку [10 базовых трасс]",
        "pt": "⚡ Apenas Sprints Ponto a Ponto [10 Pistas Base]",
        "fr": "⚡ Sprints Point à Point Uniquement [10 Circuits]",
        "de": "⚡ Nur Punkt-zu-Punkt Sprints [10 Strecken]",
    },
    "circuits": {
        "es": "🔄 Solo Circuitos Cerrados Clásicos [20 Trazados]",
        "en": "🔄 Classic Closed Circuits Only [20 Tracks]",
        "ru": "🔄 Только классические кольцевые гонки [20 трасс]",
        "pt": "🔄 Apenas Circuitos Fechados Clássicos [20 Pistas]",
        "fr": "🔄 Circuits Fermés Classiques Uniquement [20 Circuits]",
        "de": "🔄 Nur klassische Rundkurse [20 Strecken]",
    },
    "dlc_airport": {
        "es": "✈️ Solo DLC Aeropuerto Hughes (Terminal Velocity) [10 Trazados]",
        "en": "✈️ Hughes Airport DLC Only (Terminal Velocity) [10 Tracks]",
        "ru": "✈️ Только DLC Аэропорт Хьюз (Terminal Velocity) [10 трасс]",
        "pt": "✈️ Apenas DLC Aeroporto Hughes (Terminal Velocity) [10 Pistas]",
        "fr": "✈️ DLC Aéroport Hughes Uniquement (Terminal Velocity) [10 Circuits]",
        "de": "✈️ Nur Hughes Airport DLC (Terminal Velocity) [10 Strecken]",
    },
    "mixed": {
        "es": "🎲 Mix Completo (Carreras + Desafíos Originales)",
        "en": "🎲 Full Mix (Races + Original Challenges)",
        "ru": "🎲 Полный микс (Гонки + оригинальные испытания)",
        "pt": "🎲 Mix Completo (Corridas + Desafios Originais)",
        "fr": "🎲 Mix Complet (Courses + Défis Originaux)",
        "de": "🎲 Vollständiger Mix (Rennen + Original-Herausforderungen)",
    },
    "challenges": {
        "es": "🎪 Solo Desafíos y Acrobacias (Original)",
        "en": "🎪 Stunt Challenges Only (Original)",
        "ru": "🎪 Только испытания и трюки (Оригинал)",
        "pt": "🎪 Apenas Desafios e Acrobacias (Original)",
        "fr": "🎪 Défis de Cascades Uniquement (Original)",
        "de": "🎪 Nur Stunt-Herausforderungen (Original)",
    },
}

I18N = {
    "es": {
        "admin_active": "⚡ ADMINISTRADOR ACTIVO",
        "admin_missing": "⚠ SIN PERMISOS DE ADMIN",
        "player_card": "👤  IDENTIDAD DEL PILOTO",
        "player_name": "Nombre en Línea:",
        "save_name_btn": "Guardar / Actualizar en Vivo",
        "live_name_hint": "💡 Si ya estás jugando o el servidor está abierto, el nombre se cambia en vivo sin reiniciar.",
        "net_card": "🌐  MODO MULTIJUGADOR / RED",
        "mode_host": "🖥️  CREAR SESIÓN (HOST)",
        "mode_join": "🎮  UNIRSE A SESIÓN (JOIN)",
        "host_ip_lbl": "Elige tu IP para hospedar el servidor:",
        "speedlist_mode_lbl": "🏁 Modo de Speedlist / Carreras:",
        "share_ip_box": "TU IP DE SERVIDOR PARA COMPARTIR:",
        "copy_ip_btn": "📋 Copiar IP",
        "copied": "✓ IP copiada al portapapeles",
        "join_host_lbl": "IP del Host (Tu amigo con el servidor):",
        "join_my_lbl": "Tu IP de conexión en la VPN/LAN (Ej: tu Radmin):",
        "game_card": "📁  EJECUTABLE DEL JUEGO",
        "browse_btn": "Examinar…",
        "patch_btn": "🔧 Parchear NFS13.exe",
        "server_off": "● SERVIDOR DETENIDO",
        "server_on": "● SERVIDOR ACTIVO",
        "stop_srv_btn": "⏹ Detener Servidor",
        "clean_hosts_btn": "🌐 Limpiar Hosts",
        "firewall_btn": "🛡️ Firewall",
        "btn_host_play": "HOST AND PLAY",
        "btn_join_play": "PLAY",
        "hosts_err_title": "Error en Hosts",
        "hosts_err_msg": "No se pudo actualizar el archivo hosts:\n{0}\n\nAsegúrate de ejecutar el Launcher como Administrador.",
        "firewall_ok": "✓ Puertos abiertos correctamente en el Firewall de Windows (42127, 44125, 8080, 17500, 3659).",
        "firewall_err": "Error configurando firewall: {0}",
        "game_path_missing": "Por favor selecciona la ruta de NFS13.online.exe o NFS13.exe antes de iniciar.",
        "friend_ip_missing": "Por favor ingresa la IP del servidor de tu amigo.",
        "clean_hosts_confirm": "¿Deseas eliminar las redirecciones de EA del archivo hosts?",
        "clean_hosts_ok": "Archivo hosts limpiado exitosamente.",
        "stop_srv_confirm": "¿Deseas detener el servidor antes de cerrar el launcher?",
        "uac_prompt": "El Launcher necesita permisos de Administrador para configurar el archivo hosts de Windows.\n\n¿Deseas reiniciar con permisos de Administrador?",
    },
    "en": {
        "admin_active": "⚡ ADMINISTRATOR ACTIVE",
        "admin_missing": "⚠ NOT RUNNING AS ADMIN",
        "player_card": "👤  DRIVER IDENTITY",
        "player_name": "Online Driver Name:",
        "save_name_btn": "Save / Live Update",
        "live_name_hint": "💡 If already in-game or server is running, your name updates live without restart.",
        "net_card": "🌐  MULTIPLAYER / NETWORK MODE",
        "mode_host": "🖥️  HOST SESSION",
        "mode_join": "🎮  JOIN SESSION",
        "host_ip_lbl": "Select your IP to host the server:",
        "speedlist_mode_lbl": "🏁 Speedlist Race Mode:",
        "share_ip_box": "YOUR SERVER IP TO SHARE WITH FRIENDS:",
        "copy_ip_btn": "📋 Copy IP",
        "copied": "✓ IP copied to clipboard",
        "join_host_lbl": "Host IP Address (Your friend's IP):",
        "join_my_lbl": "Your connection IP on VPN/LAN (e.g. your Radmin):",
        "game_card": "📁  GAME EXECUTABLE",
        "browse_btn": "Browse…",
        "patch_btn": "🔧 Patch NFS13.exe",
        "server_off": "● SERVER STOPPED",
        "server_on": "● SERVER ACTIVE",
        "stop_srv_btn": "⏹ Stop Server",
        "clean_hosts_btn": "🌐 Clean Hosts",
        "firewall_btn": "🛡️ Firewall",
        "btn_host_play": "HOST AND PLAY",
        "btn_join_play": "PLAY",
        "hosts_err_title": "Hosts File Error",
        "hosts_err_msg": "Could not update hosts file:\n{0}\n\nMake sure the Launcher is running as Administrator.",
        "firewall_ok": "✓ Ports opened successfully in Windows Firewall (42127, 44125, 8080, 17500, 3659).",
        "firewall_err": "Error configuring firewall: {0}",
        "game_path_missing": "Please select the path to NFS13.online.exe or NFS13.exe before starting.",
        "friend_ip_missing": "Please enter your friend's server IP address.",
        "clean_hosts_confirm": "Do you want to remove all EA redirects from the hosts file?",
        "clean_hosts_ok": "Hosts file cleaned successfully.",
        "stop_srv_confirm": "Do you want to stop the server before closing the launcher?",
        "uac_prompt": "This Launcher requires Administrator privileges to configure Windows hosts redirection.\n\nRestart as Administrator?",
    },
    "ru": {
        "admin_active": "⚡ РЕЖИМ АДМИНА АКТИВЕН",
        "admin_missing": "⚠ НЕТ ПРАВ АДМИНА",
        "player_card": "👤  ПРОФИЛЬ ВОДИТЕЛЯ",
        "player_name": "Имя в сети:",
        "save_name_btn": "Сохранить / Обновить на лету",
        "live_name_hint": "💡 Если игра или сервер запущены, имя изменится в реальном времени.",
        "net_card": "🌐  СЕТЕВОЙ РЕЖИМ",
        "mode_host": "🖥️  СОЗДАТЬ СЕССИЮ (ХОСТ)",
        "mode_join": "🎮  ПОДКЛЮЧИТЬСЯ (КЛИЕНТ)",
        "host_ip_lbl": "Выберите ваш IP для запуска сервера:",
        "speedlist_mode_lbl": "🏁 Режим гонок спидлиста:",
        "share_ip_box": "ВАШ IP СЕРВЕРА ДЛЯ ДРУЗЕЙ:",
        "copy_ip_btn": "📋 Скопировать IP",
        "copied": "✓ IP скопирован в буфер",
        "join_host_lbl": "IP адрес хоста (IP вашего друга):",
        "join_my_lbl": "Ваш IP в VPN/LAN (например, Radmin):",
        "game_card": "📁  ИСПОЛНЯЕМЫЙ ФАЙЛ ИГРЫ",
        "browse_btn": "Обзор…",
        "patch_btn": "🔧 Пропатчить NFS13.exe",
        "server_off": "● СЕРВЕР ОСТАНОВЛЕН",
        "server_on": "● СЕРВЕР АКТИВЕН",
        "stop_srv_btn": "⏹ Стоп Сервер",
        "clean_hosts_btn": "🌐 Очистить Hosts",
        "firewall_btn": "🛡️ Брандмауэр",
        "btn_host_play": "HOST AND PLAY",
        "btn_join_play": "PLAY",
        "hosts_err_title": "Ошибка Hosts",
        "hosts_err_msg": "Не удалось обновить файл hosts:\n{0}\n\nЗапустите лаунчер от имени Администратора.",
        "firewall_ok": "✓ Порты успешно открыты в брандмауэре Windows (42127, 44125, 8080, 17500, 3659).",
        "firewall_err": "Ошибка брандмауэра: {0}",
        "game_path_missing": "Пожалуйста, укажите путь к NFS13.online.exe перед запуском.",
        "friend_ip_missing": "Пожалуйста, введите IP адрес сервера вашего друга.",
        "clean_hosts_confirm": "Удалить все перенаправления EA из файла hosts?",
        "clean_hosts_ok": "Файл hosts успешно очищен.",
        "stop_srv_confirm": "Остановить сервер перед закрытием лаунчера?",
        "uac_prompt": "Лаунчеру требуются права Администратора для изменения файла hosts.\n\nПерезапустить от имени Администратора?",
    },
    "pt": {
        "admin_active": "⚡ ADMINISTRADOR ATIVO",
        "admin_missing": "⚠ SEM PRIVILÉGIOS DE ADMIN",
        "player_card": "👤  IDENTIDADE DO PILOTO",
        "player_name": "Nome Online:",
        "save_name_btn": "Salvar / Atualizar ao Vivo",
        "live_name_hint": "💡 Se já estiver jogando ou o servidor estiver aberto, o nome muda ao vivo sem reiniciar.",
        "net_card": "🌐  MODO MULTIJOGADOR / REDE",
        "mode_host": "🖥️  CRIAR SESSÃO (HOST)",
        "mode_join": "🎮  ENTRAR NA SESSÃO (JOIN)",
        "host_ip_lbl": "Escolha seu IP para hospedar o servidor:",
        "speedlist_mode_lbl": "🏁 Modo de Speedlist / Corridas:",
        "share_ip_box": "SEU IP DE SERVIDOR PARA COMPARTILHAR:",
        "copy_ip_btn": "📋 Copiar IP",
        "copied": "✓ IP copiado para a área de transferência",
        "join_host_lbl": "IP do Host (Seu amigo com o servidor):",
        "join_my_lbl": "Seu IP de conexão na VPN/LAN (Ex: seu Radmin):",
        "game_card": "📁  EXECUTÁVEL DO JOGO",
        "browse_btn": "Procurar…",
        "patch_btn": "🔧 Modificar NFS13.exe",
        "server_off": "● SERVIDOR PARADO",
        "server_on": "● SERVIDOR ATIVO",
        "stop_srv_btn": "⏹ Parar Servidor",
        "clean_hosts_btn": "🌐 Limpar Hosts",
        "firewall_btn": "🛡️ Firewall",
        "btn_host_play": "HOST AND PLAY",
        "btn_join_play": "PLAY",
        "hosts_err_title": "Erro no Arquivo Hosts",
        "hosts_err_msg": "Não foi possível atualizar o arquivo hosts:\n{0}\n\nExecute o Launcher como Administrador.",
        "firewall_ok": "✓ Portas abertas com sucesso no Firewall do Windows (42127, 44125, 8080, 17500, 3659).",
        "firewall_err": "Erro no firewall: {0}",
        "game_path_missing": "Selecione o caminho do NFS13.online.exe ou NFS13.exe antes de iniciar.",
        "friend_ip_missing": "Digite o IP do servidor do seu amigo.",
        "clean_hosts_confirm": "Deseja remover as regras do NFS do arquivo hosts?",
        "clean_hosts_ok": "Arquivo hosts limpo com sucesso.",
        "stop_srv_confirm": "Deseja parar o servidor antes de fechar o launcher?",
        "uac_prompt": "O Launcher precisa de permissão de Administrador para configurar o arquivo hosts.\n\nReiniciar como Administrador?",
    },
    "fr": {
        "admin_active": "⚡ ADMINISTRATEUR ACTIF",
        "admin_missing": "⚠ SANS DROITS D'ADMIN",
        "player_card": "👤  IDENTITÉ DU PILOTE",
        "player_name": "Nom en Ligne:",
        "save_name_btn": "Enregistrer / En Direct",
        "live_name_hint": "💡 Si le serveur ou le jeu est lancé, votre nom s'actualise en direct.",
        "net_card": "🌐  MODE MULTIJOUEUR / RÉSEAU",
        "mode_host": "🖥️  HÉBERGER UNE SESSION",
        "mode_join": "🎮  REJOINDRE UNE SESSION",
        "host_ip_lbl": "Choisissez votre IP pour héberger:",
        "speedlist_mode_lbl": "🏁 Mode de Course Speedlist :",
        "share_ip_box": "VOTRE IP SERVEUR À PARTAGER:",
        "copy_ip_btn": "📋 Copier l'IP",
        "copied": "✓ IP copiée dans le presse-papiers",
        "join_host_lbl": "Adresse IP de l'hôte (Votre ami):",
        "join_my_lbl": "Votre IP sur VPN/LAN (ex: Radmin):",
        "game_card": "📁  EXÉCUTABLE DU JEU",
        "browse_btn": "Parcourir…",
        "patch_btn": "🔧 Patcher NFS13.exe",
        "server_off": "● SERVEUR ARRÊTÉ",
        "server_on": "● SERVEUR ACTIF",
        "stop_srv_btn": "⏹ Arrêter Serveur",
        "clean_hosts_btn": "🌐 Nettoyer Hosts",
        "firewall_btn": "🛡️ Pare-feu",
        "btn_host_play": "HOST AND PLAY",
        "btn_join_play": "PLAY",
        "hosts_err_title": "Erreur fichier Hosts",
        "hosts_err_msg": "Impossible de modifier hosts:\n{0}\n\nExécutez en tant qu'administrateur.",
        "firewall_ok": "✓ Ports ouverts avec succès dans le Pare-feu Windows (42127, 44125, 8080, 17500, 3659).",
        "firewall_err": "Erreur Pare-feu: {0}",
        "game_path_missing": "Veuillez sélectionner NFS13.online.exe avant de lancer.",
        "friend_ip_missing": "Veuillez entrer l'IP du serveur de votre ami.",
        "clean_hosts_confirm": "Supprimer les redirections EA du fichier hosts?",
        "clean_hosts_ok": "Fichier hosts nettoyé avec succès.",
        "stop_srv_confirm": "Voulez-vous arrêter le serveur avant de quitter?",
        "uac_prompt": "Le Launcher nécessite les droits d'administrateur pour configurer le fichier hosts.\n\nRedémarrer en Administrateur?",
    },
    "de": {
        "admin_active": "⚡ ADMINISTRATOR AKTIV",
        "admin_missing": "⚠ KEINE ADMIN-RECHTE",
        "player_card": "👤  FAHRER-IDENTITÄT",
        "player_name": "Online-Fahrername:",
        "save_name_btn": "Speichern / Live Ändern",
        "live_name_hint": "💡 Wenn das Spiel oder der Server läuft, wird der Name sofort live geändert.",
        "net_card": "🌐  MEHRSPIELER / NETZWERKMODUS",
        "mode_host": "🖥️  SESSION HOSTEN",
        "mode_join": "🎮  SESSION BEITRETEN",
        "host_ip_lbl": "Wählen Sie Ihre IP zum Hosten:",
        "speedlist_mode_lbl": "🏁 Speedlist-Rennmodus:",
        "share_ip_box": "IHRE SERVER-IP ZUM TEILEN:",
        "copy_ip_btn": "📋 IP Kopieren",
        "copied": "✓ IP in die Zwischenablage kopiert",
        "join_host_lbl": "Host-IP-Adresse (Ihr Freund):",
        "join_my_lbl": "Ihre Verbindungs-IP in VPN/LAN (z. B. Radmin):",
        "game_card": "📁  SPIEL-DATEI",
        "browse_btn": "Durchsuchen…",
        "patch_btn": "🔧 NFS13.exe Patchen",
        "server_off": "● SERVER GESTOPPT",
        "server_on": "● SERVER AKTIV",
        "stop_srv_btn": "⏹ Server Stoppen",
        "clean_hosts_btn": "🌐 Hosts Bereinigen",
        "firewall_btn": "🛡️ Firewall",
        "btn_host_play": "HOST AND PLAY",
        "btn_join_play": "PLAY",
        "hosts_err_title": "Hosts-Datei Fehler",
        "hosts_err_msg": "Hosts-Datei konnte nicht aktualisiert werden:\n{0}\n\nBitte als Administrator ausführen.",
        "firewall_ok": "✓ Ports in der Windows-Firewall erfolgreich geöffnet (42127, 44125, 8080, 17500, 3659).",
        "firewall_err": "Firewall-Fehler: {0}",
        "game_path_missing": "Bitte wählen Sie vor dem Start NFS13.online.exe aus.",
        "friend_ip_missing": "Bitte geben Sie die Server-IP Ihres Freundes ein.",
        "clean_hosts_confirm": "Möchten Sie alle EA-Einträge aus der Hosts-Datei entfernen?",
        "clean_hosts_ok": "Hosts-Datei erfolgreich bereinigt.",
        "stop_srv_confirm": "Möchten Sie den Server vor dem Beenden stoppen?",
        "uac_prompt": "Der Launcher benötigt Administratorrechte, um die Hosts-Datei anzupassen.\n\nAls Administrator neu starten?",
    }
}


# ─────────────────────────── UAC Admin Check ─────────────────────────────────

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    """Re-launch the launcher with UAC elevation."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        params = " ".join(f'"{a}"' for a in sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
    else:
        script = str(Path(sys.argv[0]).resolve())
        params = " ".join(f'"{a}"' for a in sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas",
            sys.executable,
            f'"{script}" {params}'.strip(),
            None, 1
        )


def find_python() -> str:
    """Find the real python.exe on the system."""
    if not getattr(sys, "frozen", False):
        return sys.executable
    py = shutil.which("python")
    if py and "WindowsApps" not in py:
        return py
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Python" / "pythoncore-3.15-64" / "python.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python313" / "python.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "python.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python311" / "python.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python310" / "python.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Python313" / "python.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Python312" / "python.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Python311" / "python.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Python310" / "python.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    py_launcher = shutil.which("py")
    if py_launcher:
        return py_launcher
    return "python"


# ─────────────────────────── Config Persistence ──────────────────────────────

def save_speedlist_mode_json(mode_key: str):
    """Write speedlist_mode.json so the backend server reads the chosen event pool."""
    targets = [
        BASE_DIR / "server" / "speedlist_mode.json",
        BASE_DIR / "speedlist_mode.json",
        RESOURCE_DIR / "server" / "speedlist_mode.json",
        RESOURCE_DIR / "speedlist_mode.json",
    ]
    for t in targets:
        try:
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_text(json.dumps({"mode": mode_key}, indent=2), encoding="utf-8")
        except Exception:
            pass
    os.environ["NFS13_SPEEDLIST_MODE"] = mode_key


def load_config() -> dict:
    cfg = configparser.ConfigParser()
    data = {
        "player_name": "Player1",
        "game_path": "",
        "mode": "host",
        "host_ip": "",
        "join_ip": "",
        "my_ip": "",
        "speedlist_mode": "all_races",
        "language": "en",
    }
    if LAUNCHER_INI.exists():
        try:
            cfg.read(LAUNCHER_INI, encoding="utf-8")
            section = None
            if "settings" in cfg:
                section = cfg["settings"]
            elif "launcher" in cfg:
                section = cfg["launcher"]

            if section:
                data["player_name"]    = section.get("player_name", section.get("name", "Player1"))
                data["game_path"]      = section.get("game_path", "")
                data["mode"]           = section.get("mode", "host")
                data["host_ip"]        = section.get("host_ip", section.get("last_host_ip", ""))
                data["join_ip"]        = section.get("join_ip", section.get("last_host_ip", ""))
                data["my_ip"]          = section.get("my_ip", section.get("last_my_ip", ""))
                data["speedlist_mode"] = section.get("speedlist_mode", "all_races")
                data["language"]       = section.get("language", "en")
        except Exception:
            pass

    # Auto-detect game only if launcher is placed inside game directory
    if not data["game_path"]:
        auto_candidates = [
            BASE_DIR / "NFS13.online.exe",
            BASE_DIR / "NFS13.exe",
        ]
        for c in auto_candidates:
            if c.exists():
                data["game_path"] = str(c)
                break

    return data


def save_config(data: dict):
    cfg = configparser.ConfigParser()
    cfg["settings"] = {
        "player_name":    data.get("player_name", "Player1"),
        "game_path":      data.get("game_path", ""),
        "mode":           data.get("mode", "host"),
        "host_ip":        data.get("host_ip", ""),
        "join_ip":        data.get("join_ip", ""),
        "my_ip":          data.get("my_ip", ""),
        "speedlist_mode": data.get("speedlist_mode", "all_races"),
        "language":       data.get("language", "en"),
    }
    cfg["launcher"] = {
        "game_path":      data.get("game_path", ""),
        "player_name":    data.get("player_name", "Player1"),
        "last_host_ip":   data.get("host_ip", "") or data.get("join_ip", ""),
        "last_my_ip":     data.get("my_ip", ""),
        "speedlist_mode": data.get("speedlist_mode", "all_races"),
        "language":       data.get("language", "en"),
    }
    try:
        with open(LAUNCHER_INI, "w", encoding="utf-8") as f:
            cfg.write(f)
    except Exception as exc:
        print(f"Error saving launcher.ini: {exc}", file=sys.stderr)


# ─────────────────────────── IP Detection ────────────────────────────────────

def get_all_ips():
    """Parse ipconfig output and classify network adapters."""
    try:
        output = subprocess.check_output("ipconfig", shell=True).decode(errors="ignore")
    except Exception:
        return []

    adapters = []
    current_adapter = None
    for line in output.splitlines():
        stripped = line.strip()
        if stripped and not line.startswith(" ") and ":" in stripped:
            current_adapter = stripped.rstrip(":").strip()
        if "IPv4" in stripped and current_adapter:
            ip = stripped.split(":")[-1].strip()
            if ip and ip[0].isdigit():
                adapters.append((current_adapter, ip))
    return adapters


def classify_ip(ip: str) -> tuple[str, str]:
    if ip.startswith("26."):
        return "RADMIN VPN", "🎮"
    elif ip.startswith("25."):
        return "HAMACHI", "🔗"
    elif ip.startswith("100."):
        return "TAILSCALE", "🔒"
    elif ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        return "LAN / WI-FI", "🏠"
    elif ip.startswith("127."):
        return "LOCAL", "💻"
    else:
        return "NET", "🌐"


# ─────────────────────────── Hosts Management ────────────────────────────────

def update_hosts_file(target_ip: str) -> str:
    """Redirect EA domains in C:\\Windows\\System32\\drivers\\etc\\hosts."""
    try:
        if HOSTS_FILE.exists():
            original = HOSTS_FILE.read_text(encoding="utf-8", errors="replace")
        else:
            original = ""

        # Clean existing NFSMW block
        lines = original.splitlines()
        cleaned = []
        skip = False
        for line in lines:
            if HOSTS_TAG in line:
                skip = True
            if skip:
                stripped = line.strip()
                is_ea = any(d in stripped for d in EA_DOMAINS)
                if not is_ea and HOSTS_TAG not in stripped:
                    skip = False
                    if stripped:
                        cleaned.append(line)
            else:
                cleaned.append(line)

        final_cleaned = [l for l in cleaned if not any(d in l for d in EA_DOMAINS)]

        # Append new redirect block
        new_block = ["", HOSTS_TAG]
        for domain in EA_DOMAINS:
            new_block.append(f"{target_ip} {domain}")
        new_block.append(f"{HOSTS_TAG} END")
        new_block.append("")

        content = "\n".join(final_cleaned).rstrip("\n") + "\n" + "\n".join(new_block)
        HOSTS_FILE.write_text(content, encoding="utf-8")
        return ""
    except PermissionError:
        return "Permission denied editing hosts file. Run as Administrator."
    except Exception as exc:
        return str(exc)


def remove_hosts_entries() -> str:
    """Clean all EA domain redirects from hosts file."""
    try:
        if not HOSTS_FILE.exists():
            return ""
        original = HOSTS_FILE.read_text(encoding="utf-8", errors="replace")
        lines = original.splitlines()
        final = []
        in_block = False
        for line in lines:
            if HOSTS_TAG in line:
                in_block = True
                continue
            if in_block:
                stripped = line.strip()
                if not any(d in stripped for d in EA_DOMAINS):
                    in_block = False
                    if stripped:
                        final.append(line)
                continue
            if any(d in line for d in EA_DOMAINS):
                continue
            final.append(line)
        HOSTS_FILE.write_text("\n".join(final) + "\n", encoding="utf-8")
        return ""
    except Exception as exc:
        return str(exc)


# ─────────────────────────── Native Firewall Rules ───────────────────────────

def setup_windows_firewall() -> tuple[bool, str]:
    """Native firewall configuration without needing external .bat files."""
    rules = [
        ("NFSMW12 - Blaze SSL", "TCP", "42127"),
        ("NFSMW12 - HTTPS SSL", "TCP", "44125"),
        ("NFSMW12 - Autolog HTTP", "TCP", "8080"),
        ("NFSMW12 - QoS TCP", "TCP", "17500"),
        ("NFSMW12 - QoS UDP", "UDP", "17500"),
        ("NFSMW12 - P2P Mesh UDP", "UDP", "3659"),
    ]
    try:
        for name, proto, port in rules:
            cmd = f'netsh advfirewall firewall add rule name="{name}" dir=in action=allow protocol={proto} localport={port} profile=any'
            subprocess.run(cmd, shell=True, capture_output=True)
        return True, ""
    except Exception as exc:
        return False, str(exc)


# ─────────────────────────── Live Player Rename ──────────────────────────────

def send_player_rename(name: str, host_ip: str = "127.0.0.1") -> tuple[bool, str]:
    """Apply name via HTTP /rename API and update players.json."""
    import re
    if not name or not re.match(r"^[A-Za-z0-9_-]{1,15}$", name):
        return False, "1-15 chars: [A-Z, a-z, 0-9, _, -]"

    try:
        if PLAYERS_JSON.exists():
            p_data = json.loads(PLAYERS_JSON.read_text(encoding="utf-8"))
            if isinstance(p_data, list) and p_data:
                p_data[0]["name"] = name
            elif isinstance(p_data, dict):
                p_data["name"] = name
            PLAYERS_JSON.write_text(json.dumps(p_data, indent=2), encoding="utf-8")
    except Exception:
        pass

    try:
        url = f"http://{host_ip}:8080/rename?name={urllib.parse.quote(name)}"
        req = urllib.request.Request(url, headers={"User-Agent": "NFSMW-Launcher"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                return True, f"✓ {name} (Live)"
    except Exception:
        pass

    return True, f"✓ {name} (Saved)"


# ─────────────────────────── Native Game Patcher ─────────────────────────────

def apply_nfs13_patch(src: Path) -> tuple[bool, str, Path | None]:
    """Applies binary patch natively without needing external python process."""
    patch_candidates = [
        RESOURCE_DIR / "client" / "patches" / "nfs13_online.json",
        BASE_DIR / "client" / "patches" / "nfs13_online.json",
        RESOURCE_DIR / "patches" / "nfs13_online.json",
        BASE_DIR / "patches" / "nfs13_online.json",
    ]
    patch_file = None
    for c in patch_candidates:
        if c.exists():
            patch_file = c
            break

    if not patch_file:
        return False, "Patch data file (nfs13_online.json) not found.", None

    try:
        import hashlib
        patch = json.loads(patch_file.read_text(encoding="utf-8"))
        # If the user selected NFS13.online.exe instead of NFS13.exe, fall back
        # automatically to the sibling clean NFS13.exe when available.
        if src.name.lower() == "nfs13.online.exe":
            sibling_base = src.with_name("NFS13.exe")
            if sibling_base.exists():
                src = sibling_base

        data = bytearray(src.read_bytes())
        digest = hashlib.sha256(data).hexdigest()

        out_path = src.with_name("NFS13.online.exe")
        if digest == patch["patched_sha256"]:
            if src.resolve() != out_path.resolve():
                out_path.write_bytes(data)
            return True, "This executable is already patched and up to date!", out_path

        if len(data) != patch["size"] or digest != patch["base_sha256"]:
            return False, (
                f"Unsupported executable version.\n\n"
                f"Expected size: {patch['size']} bytes (got {len(data)})\n"
                f"Expected SHA256: {patch['base_sha256'][:16]}...\n"
                f"Your file SHA256: {digest[:16]}..."
            ), None

        for item in patch["patches"]:
            offset = int(item["offset"], 16)
            original = bytes.fromhex(item["original"])
            patched = bytes.fromhex(item["patched"])
            if data[offset:offset + len(original)] != original:
                return False, f"Unexpected byte signature at offset {item['offset']}", None
            data[offset:offset + len(patched)] = patched

        result = hashlib.sha256(data).hexdigest()
        if result != patch["patched_sha256"]:
            return False, "Patched file verification failed (hash mismatch).", None

        out_path.write_bytes(data)
        return True, f"NFS13.online.exe created successfully!\n\nLocation:\n{out_path}", out_path
    except Exception as exc:
        return False, str(exc), None


# ─────────────────────────── Modern GUI Widgets ──────────────────────────────

class ModernCard(tk.Frame):
    """Clean white card with subtle border and crisp padding."""
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG_WHITE, bd=1, relief="solid",
                         highlightbackground=BORDER_LIGHT, highlightthickness=1, **kw)


class ActionButton(tk.Button):
    """Stylized Criterion button with red hover effect."""
    def __init__(self, master, text="", command=None, bg=RED_PRIMARY, fg=TEXT_WHITE,
                 hover_bg=RED_HOVER, font=None, padx=16, pady=9, **kw):
        self._bg = bg
        self._hover = hover_bg
        super().__init__(master, text=text, command=command, bg=bg, fg=fg,
                         activebackground=hover_bg, activeforeground=TEXT_WHITE,
                         font=font or ("Segoe UI", 10, "bold"),
                         bd=0, relief="flat", cursor="hand2", padx=padx, pady=pady, **kw)
        self.bind("<Enter>", lambda e: super(ActionButton, self).configure(bg=self._hover))
        self.bind("<Leave>", lambda e: super(ActionButton, self).configure(bg=self._bg))

    def configure(self, cnf=None, **kw):
        if "hover_bg" in kw:
            self._hover = kw.pop("hover_bg")
            kw.setdefault("activebackground", self._hover)
        if "bg" in kw:
            self._bg = kw["bg"]
        return super().configure(cnf, **kw)

    config = configure


class SecondaryButton(tk.Button):
    """Clean outline secondary button."""
    def __init__(self, master, text="", command=None, padx=12, pady=6, **kw):
        super().__init__(master, text=text, command=command,
                         bg="#FFFFFF", fg=TEXT_DARK,
                         activebackground="#F1F3F7", activeforeground=RED_PRIMARY,
                         font=("Segoe UI", 9, "bold"),
                         bd=1, relief="solid", highlightbackground=BORDER_LIGHT,
                         highlightthickness=1, cursor="hand2", padx=padx, pady=pady, **kw)
        self.bind("<Enter>", lambda e: self.config(bg="#F8F9FA", fg=RED_PRIMARY))
        self.bind("<Leave>", lambda e: self.config(bg="#FFFFFF", fg=TEXT_DARK))


# ─────────────────────────── Main Application ────────────────────────────────

class NFSMWLauncher(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Need for Speed: Most Wanted (2012) — Private Server Launcher")
        self.resizable(True, True)
        self.configure(bg=BG_MAIN)

        # Set official icon
        if ICON_FILE.exists():
            try:
                self.iconbitmap(str(ICON_FILE))
            except Exception:
                pass

        self.cfg = load_config()
        self.lang = self.cfg.get("language", "en")
        if self.lang not in I18N:
            self.lang = "en"

        self._server_proc = None
        self._ips = get_all_ips()

        self._build_ui()
        self._fit_window(center=True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key: str) -> str:
        """Get translated string for current language."""
        return I18N.get(self.lang, I18N["en"]).get(key, key)

    def _fit_window(self, center: bool = False):
        """Auto-size window to fit all cards + footer cleanly across DPI scales."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        req_w = max(900, self.winfo_reqwidth())
        req_h = max(680, self.winfo_reqheight() + 6)
        w = min(req_w, max(860, sw - 40))
        h = min(req_h, max(660, sh - 60))
        self.minsize(860, h)
        if center:
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2 - 12)
            self.geometry(f"{w}x{h}+{x}+{y}")
        else:
            cur_w = max(w, self.winfo_width())
            cur_h = max(h, self.winfo_height())
            if cur_w != self.winfo_width() or cur_h != self.winfo_height():
                self.geometry(f"{cur_w}x{cur_h}")

    # ─────────────────────── UI Construction ─────────────────────────────────

    def _build_ui(self):
        # 1. Top Red Accent Line
        tk.Frame(self, bg=RED_PRIMARY, height=4).pack(fill="x")

        # 2. Header (Criterion Branding)
        header = tk.Frame(self, bg=BG_WHITE, height=76, padx=28)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Titles
        title_box = tk.Frame(header, bg=BG_WHITE)
        title_box.pack(side="left", fill="y", pady=12)

        tk.Label(title_box, text="NEED FOR SPEED™", bg=BG_WHITE, fg=RED_PRIMARY,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(title_box, text="MOST WANTED", bg=BG_WHITE, fg=TEXT_DARK,
                 font=("Impact", 21)).pack(anchor="w", pady=(0, 0))

        # Right Controls: Language Selector & Admin Badge
        right_box = tk.Frame(header, bg=BG_WHITE)
        right_box.pack(side="right", fill="y", pady=16)

        # Language Selector
        lang_frame = tk.Frame(right_box, bg=BG_WHITE)
        lang_frame.pack(side="right", padx=(12, 0))

        self._lang_var = tk.StringVar(value=LANGUAGES.get(self.lang, "🇺🇸 English"))
        self._lang_combo = ttk.Combobox(
            lang_frame, textvariable=self._lang_var,
            values=list(LANGUAGES.values()),
            state="readonly", font=("Segoe UI", 9, "bold"), width=14
        )
        self._lang_combo.pack(side="right", ipady=3)
        self._lang_combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        # Admin Badge
        admin_text = self._t("admin_active") if is_admin() else self._t("admin_missing")
        admin_bg   = GREEN_BG if is_admin() else RED_TINT
        admin_fg   = GREEN_SUCCESS if is_admin() else RED_PRIMARY
        admin_bd   = GREEN_BORDER if is_admin() else RED_BORDER

        self._admin_badge = tk.Label(right_box, text=admin_text, bg=admin_bg, fg=admin_fg,
                                     font=("Segoe UI", 8, "bold"), padx=10, pady=4,
                                     bd=1, relief="solid", highlightbackground=admin_bd, highlightthickness=1)
        self._admin_badge.pack(side="right", padx=(8, 0))

        # Divider line
        tk.Frame(self, bg=BORDER_LIGHT, height=1).pack(fill="x")

        # 3. Bottom Action Bar & Status (packed BEFORE main container so Tkinter
        #    ALWAYS reserves the full footer height and never clips HOST AND PLAY!)
        footer = tk.Frame(self, bg=BG_WHITE, padx=28, pady=12)
        footer.pack(fill="x", side="bottom")
        tk.Frame(self, bg=BORDER_LIGHT, height=1).pack(fill="x", side="bottom")

        # Server status & utility buttons on left
        srv_box = tk.Frame(footer, bg=BG_WHITE)
        srv_box.pack(side="left", anchor="center")

        self._srv_status_pill = tk.Label(srv_box, text=self._t("server_off"),
                                         bg="#F1F3F6", fg=TEXT_MUTED,
                                         font=("Segoe UI", 8, "bold"), padx=10, pady=6,
                                         bd=1, relief="solid", highlightbackground=BORDER_LIGHT, highlightthickness=1)
        self._srv_status_pill.pack(side="left", padx=(0, 8))

        self._stop_srv_btn = SecondaryButton(srv_box, text=self._t("stop_srv_btn"), command=self._stop_server)

        self._btn_clean_hosts = SecondaryButton(srv_box, text=self._t("clean_hosts_btn"), command=self._clean_hosts)
        self._btn_clean_hosts.pack(side="left", padx=(0, 6))

        self._btn_firewall = SecondaryButton(srv_box, text=self._t("firewall_btn"), command=self._configure_firewall_native)
        self._btn_firewall.pack(side="left")

        # Big Main Action Button on right (natural height, never clipped)
        self._play_btn = ActionButton(
            footer, text="HOST AND PLAY",
            command=self._on_launch_clicked,
            bg=RED_PRIMARY, hover_bg=RED_HOVER,
            font=("Impact", 15), padx=34, pady=8
        )
        self._play_btn.pack(side="right", anchor="center")

        # 4. Main Content Container
        container = tk.Frame(self, bg=BG_MAIN, padx=28, pady=14)
        container.pack(fill="both", expand=True)

        # ── CARD 1: PERFIL DEL PILOTO ────────────────────────────────────
        c1 = ModernCard(container, padx=20, pady=12)
        c1.pack(fill="x", pady=(0, 10))

        c1_head = tk.Frame(c1, bg=BG_WHITE)
        c1_head.pack(fill="x", pady=(0, 8))
        self._lbl_card1_title = tk.Label(c1_head, text=self._t("player_card"), bg=BG_WHITE, fg=RED_PRIMARY,
                                         font=("Segoe UI", 10, "bold"))
        self._lbl_card1_title.pack(side="left")

        self._name_status_lbl = tk.Label(c1_head, text="", bg=BG_WHITE, fg=GREEN_SUCCESS,
                                         font=("Segoe UI", 8, "bold"))
        self._name_status_lbl.pack(side="right")

        c1_row = tk.Frame(c1, bg=BG_WHITE)
        c1_row.pack(fill="x")

        self._lbl_player_name = tk.Label(c1_row, text=self._t("player_name"), bg=BG_WHITE, fg=TEXT_BODY,
                                         font=("Segoe UI", 9, "bold"))
        self._lbl_player_name.pack(side="left", padx=(0, 12))

        self._player_var = tk.StringVar(value=self.cfg.get("player_name", "Player1"))
        self._player_entry = tk.Entry(c1_row, textvariable=self._player_var, bg=BG_INPUT, fg=TEXT_DARK,
                                      font=("Segoe UI", 10, "bold"), bd=1, relief="solid",
                                      highlightbackground=BORDER_LIGHT, highlightthickness=1, width=22)
        self._player_entry.pack(side="left", ipady=5, padx=(0, 10))

        self._btn_save_name = ActionButton(c1_row, text=self._t("save_name_btn"),
                                           command=self._on_save_player_name,
                                           bg=RED_PRIMARY, font=("Segoe UI", 9, "bold"))
        self._btn_save_name.pack(side="left")

        self._lbl_live_hint = tk.Label(c1, text=self._t("live_name_hint"),
                                       bg=BG_WHITE, fg=TEXT_MUTED, font=("Segoe UI", 8, "italic"))
        self._lbl_live_hint.pack(anchor="w", pady=(6, 0))

        # ── CARD 2: MODO MULTIJUGADOR / RED ──────────────────────────────
        c2 = ModernCard(container, padx=20, pady=14)
        c2.pack(fill="x", pady=(0, 10))

        self._lbl_card2_title = tk.Label(c2, text=self._t("net_card"), bg=BG_WHITE, fg=RED_PRIMARY,
                                         font=("Segoe UI", 10, "bold"))
        self._lbl_card2_title.pack(anchor="w", pady=(0, 10))

        # Mode Selection Segment Buttons
        mode_bar = tk.Frame(c2, bg="#F1F3F6", padx=3, pady=3, bd=1, relief="solid",
                            highlightbackground=BORDER_LIGHT, highlightthickness=1)
        mode_bar.pack(fill="x", pady=(0, 14))

        saved_mode = self.cfg.get("mode", "host")
        if saved_mode not in ("host", "join"):
            saved_mode = "host"
        self._mode_var = tk.StringVar(value=saved_mode)
        self._mode_btns = {}

        modes = [
            ("host", self._t("mode_host")),
            ("join", self._t("mode_join")),
        ]

        for m_id, m_text in modes:
            btn = tk.Label(mode_bar, text=m_text, font=("Segoe UI", 9, "bold"),
                           cursor="hand2", padx=20, pady=8)
            btn.pack(side="left", expand=True, fill="both")
            btn.bind("<Button-1>", lambda e, mid=m_id: self._select_mode(mid))
            self._mode_btns[m_id] = btn

        # Mode Dynamic Content Frames
        self._mode_content = tk.Frame(c2, bg=BG_WHITE)
        self._mode_content.pack(fill="x")

        self._build_host_subpanel(self._mode_content)
        self._build_join_subpanel(self._mode_content)

        # ── CARD 3: EJECUTABLE DEL JUEGO ─────────────────────────────────
        c3 = ModernCard(container, padx=20, pady=14)
        c3.pack(fill="x")

        self._lbl_card3_title = tk.Label(c3, text=self._t("game_card"), bg=BG_WHITE, fg=RED_PRIMARY,
                                         font=("Segoe UI", 10, "bold"))
        self._lbl_card3_title.pack(anchor="w", pady=(0, 8))

        c3_row = tk.Frame(c3, bg=BG_WHITE)
        c3_row.pack(fill="x")

        self._game_path_var = tk.StringVar(value=self.cfg.get("game_path", ""))
        self._game_entry = tk.Entry(c3_row, textvariable=self._game_path_var, bg=BG_INPUT, fg=TEXT_DARK,
                                    font=("Segoe UI", 9), bd=1, relief="solid",
                                    highlightbackground=BORDER_LIGHT, highlightthickness=1)
        self._game_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))

        self._btn_browse = SecondaryButton(c3_row, text=self._t("browse_btn"), command=self._browse_game)
        self._btn_browse.pack(side="left", padx=(0, 6))

        self._btn_patch = SecondaryButton(c3_row, text=self._t("patch_btn"), command=self._do_patch)
        self._btn_patch.pack(side="left")

        # Update mode UI after _play_btn exists
        self._update_mode_ui()

    # ─────────────────────── Mode Subpanels ──────────────────────────────────

    def _build_host_subpanel(self, parent):
        self._p_host = tk.Frame(parent, bg=BG_WHITE)

        self._lbl_host_ip_prompt = tk.Label(self._p_host, text=self._t("host_ip_lbl"),
                                            bg=BG_WHITE, fg=TEXT_DARK, font=("Segoe UI", 9, "bold"))
        self._lbl_host_ip_prompt.pack(anchor="w", pady=(0, 4))

        # Dropdown / List of interfaces
        ip_options = []
        default_choice = None
        saved_host_ip = self.cfg.get("host_ip", "")

        for adapter, ip in self._ips:
            tag, icon = classify_ip(ip)
            label = f"{icon} [{tag}]  {ip}  —  {adapter}"
            ip_options.append((ip, label))
            if ip == saved_host_ip:
                default_choice = label

        if not default_choice and ip_options:
            radmin = [lbl for ip, lbl in ip_options if ip.startswith("26.")]
            default_choice = radmin[0] if radmin else ip_options[0][1]

        self._host_ip_var = tk.StringVar(value=default_choice or "")

        cb_frame = tk.Frame(self._p_host, bg=BG_WHITE)
        cb_frame.pack(fill="x", pady=(0, 10))

        self._host_combo = ttk.Combobox(
            cb_frame, textvariable=self._host_ip_var,
            values=[lbl for _, lbl in ip_options],
            state="readonly", font=("Segoe UI", 9), height=8
        )
        self._host_combo.pack(fill="x", ipady=4)
        self._host_combo.bind("<<ComboboxSelected>>", self._on_host_combo_changed)

        # Highlight box for friend sharing
        share_box = tk.Frame(self._p_host, bg=RED_TINT, bd=1, relief="solid",
                             highlightbackground=RED_BORDER, highlightthickness=1, padx=14, pady=10)
        share_box.pack(fill="x")

        self._lbl_share_box_title = tk.Label(share_box, text=self._t("share_ip_box"), bg=RED_TINT, fg=RED_PRIMARY,
                                             font=("Segoe UI", 8, "bold"))
        self._lbl_share_box_title.pack(anchor="w")

        share_row = tk.Frame(share_box, bg=RED_TINT)
        share_row.pack(fill="x", pady=(2, 0))

        self._share_ip_lbl = tk.Label(share_row, text=self._extract_ip(self._host_ip_var.get()) or "0.0.0.0",
                                      bg=RED_TINT, fg=TEXT_DARK, font=("Consolas", 15, "bold"))
        self._share_ip_lbl.pack(side="left")

        self._btn_copy_ip = SecondaryButton(share_row, text=self._t("copy_ip_btn"), command=self._copy_share_ip)
        self._btn_copy_ip.pack(side="right")

        # Speedlist Mode Selector
        self._lbl_speedlist_prompt = tk.Label(self._p_host, text=self._t("speedlist_mode_lbl"),
                                              bg=BG_WHITE, fg=TEXT_DARK, font=("Segoe UI", 9, "bold"))
        self._lbl_speedlist_prompt.pack(anchor="w", pady=(12, 4))

        saved_sl_mode = self.cfg.get("speedlist_mode", "all_races")
        if saved_sl_mode not in SPEEDLIST_MODES:
            saved_sl_mode = "all_races"

        self._speedlist_var = tk.StringVar(value=self._get_speedlist_label(saved_sl_mode))
        self._speedlist_combo = ttk.Combobox(
            self._p_host, textvariable=self._speedlist_var,
            values=[self._get_speedlist_label(k) for k in SPEEDLIST_MODES.keys()],
            state="readonly", font=("Segoe UI", 9), height=8
        )
        self._speedlist_combo.pack(fill="x", ipady=4)
        self._speedlist_combo.bind("<<ComboboxSelected>>", self._on_speedlist_combo_changed)

    def _build_join_subpanel(self, parent):
        self._p_join = tk.Frame(parent, bg=BG_WHITE)

        row1 = tk.Frame(self._p_join, bg=BG_WHITE)
        row1.pack(fill="x", pady=(0, 10))

        self._lbl_join_host_prompt = tk.Label(row1, text=self._t("join_host_lbl"), bg=BG_WHITE, fg=TEXT_DARK,
                                              font=("Segoe UI", 9, "bold"))
        self._lbl_join_host_prompt.pack(anchor="w", pady=(0, 4))

        self._join_host_var = tk.StringVar(value=self.cfg.get("join_ip", ""))
        self._join_entry = tk.Entry(row1, textvariable=self._join_host_var, bg=BG_INPUT, fg=TEXT_DARK,
                                    font=("Consolas", 11, "bold"), bd=1, relief="solid",
                                    highlightbackground=BORDER_LIGHT, highlightthickness=1)
        self._join_entry.pack(fill="x", ipady=5)
        self._join_entry.bind("<FocusOut>", lambda e: self._save_state())

        row2 = tk.Frame(self._p_join, bg=BG_WHITE)
        row2.pack(fill="x")

        self._lbl_join_my_prompt = tk.Label(row2, text=self._t("join_my_lbl"), bg=BG_WHITE, fg=TEXT_DARK,
                                            font=("Segoe UI", 9, "bold"))
        self._lbl_join_my_prompt.pack(anchor="w", pady=(0, 4))

        ip_options = []
        default_choice = None
        saved_my_ip = self.cfg.get("my_ip", "")

        for adapter, ip in self._ips:
            tag, icon = classify_ip(ip)
            label = f"{icon} [{tag}]  {ip}  —  {adapter}"
            ip_options.append((ip, label))
            if ip == saved_my_ip:
                default_choice = label

        if not default_choice and ip_options:
            radmin = [lbl for ip, lbl in ip_options if ip.startswith("26.")]
            default_choice = radmin[0] if radmin else ip_options[0][1]

        self._join_my_ip_var = tk.StringVar(value=default_choice or "")
        self._join_my_combo = ttk.Combobox(
            row2, textvariable=self._join_my_ip_var,
            values=[lbl for _, lbl in ip_options],
            state="readonly", font=("Segoe UI", 9), height=8
        )
        self._join_my_combo.pack(fill="x", ipady=4)

    # ─────────────────────── Mode Switching ──────────────────────────────────

    def _select_mode(self, mode: str):
        self._mode_var.set(mode)
        self._update_mode_ui()
        self._save_state()

    def _update_mode_ui(self):
        curr = self._mode_var.get()
        if curr not in ("host", "join"):
            curr = "host"
            self._mode_var.set("host")

        for mid, btn in self._mode_btns.items():
            if mid == curr:
                btn.config(bg=RED_PRIMARY, fg=TEXT_WHITE)
            else:
                btn.config(bg="#F1F3F6", fg=TEXT_MUTED)

        # Show appropriate subpanel
        self._p_host.pack_forget()
        self._p_join.pack_forget()

        if hasattr(self, "_play_btn"):
            if curr == "host":
                self._p_host.pack(fill="x")
                self._play_btn.config(text=self._t("btn_host_play"))
            else:
                self._p_join.pack(fill="x")
                self._play_btn.config(text=self._t("btn_join_play"))
            self._fit_window(center=False)
        else:
            if curr == "host":
                self._p_host.pack(fill="x")
            else:
                self._p_join.pack(fill="x")

    # ─────────────────────── Language Switching ──────────────────────────────

    def _on_language_changed(self, _=None):
        val = self._lang_var.get()
        for code, label in LANGUAGES.items():
            if label == val:
                self.lang = code
                break
        self.cfg["language"] = self.lang
        self._save_state()
        self._refresh_translations()

    def _refresh_translations(self):
        """Update all text in the UI to match the new language."""
        admin_text = self._t("admin_active") if is_admin() else self._t("admin_missing")
        self._admin_badge.config(text=admin_text)

        self._lbl_card1_title.config(text=self._t("player_card"))
        self._lbl_player_name.config(text=self._t("player_name"))
        self._btn_save_name.config(text=self._t("save_name_btn"))
        self._lbl_live_hint.config(text=self._t("live_name_hint"))

        self._lbl_card2_title.config(text=self._t("net_card"))
        self._mode_btns["host"].config(text=self._t("mode_host"))
        self._mode_btns["join"].config(text=self._t("mode_join"))

        self._lbl_host_ip_prompt.config(text=self._t("host_ip_lbl"))
        self._lbl_share_box_title.config(text=self._t("share_ip_box"))
        self._btn_copy_ip.config(text=self._t("copy_ip_btn"))
        if hasattr(self, "_lbl_speedlist_prompt"):
            self._lbl_speedlist_prompt.config(text=self._t("speedlist_mode_lbl"))
            curr_sl_key = self.cfg.get("speedlist_mode", "all_races")
            self._speedlist_combo.config(values=[self._get_speedlist_label(k) for k in SPEEDLIST_MODES.keys()])
            self._speedlist_var.set(self._get_speedlist_label(curr_sl_key))

        self._lbl_join_host_prompt.config(text=self._t("join_host_lbl"))
        self._lbl_join_my_prompt.config(text=self._t("join_my_lbl"))

        self._lbl_card3_title.config(text=self._t("game_card"))
        self._btn_browse.config(text=self._t("browse_btn"))
        self._btn_patch.config(text=self._t("patch_btn"))

        if not self._server_proc or self._server_proc.poll() is not None:
            self._srv_status_pill.config(text=self._t("server_off"))
        self._stop_srv_btn.config(text=self._t("stop_srv_btn"))
        self._btn_clean_hosts.config(text=self._t("clean_hosts_btn"))
        self._btn_firewall.config(text=self._t("firewall_btn"))

        self._update_mode_ui()

    # ─────────────────────── Helpers & Actions ───────────────────────────────

    def _get_speedlist_label(self, mode_key: str) -> str:
        entry = SPEEDLIST_MODES.get(mode_key, SPEEDLIST_MODES["all_races"])
        return entry.get(self.lang, entry["en"])

    def _get_speedlist_key_from_label(self, label: str) -> str:
        for k in SPEEDLIST_MODES.keys():
            if self._get_speedlist_label(k) == label:
                return k
        return "all_races"

    def _on_speedlist_combo_changed(self, _=None):
        key = self._get_speedlist_key_from_label(self._speedlist_var.get())
        self.cfg["speedlist_mode"] = key
        save_speedlist_mode_json(key)
        self._save_state()

    def _extract_ip(self, combo_str: str) -> str:
        if not combo_str:
            return ""
        import re
        m = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", combo_str)
        return m.group(0) if m else ""

    def _on_host_combo_changed(self, _=None):
        ip = self._extract_ip(self._host_ip_var.get())
        self._share_ip_lbl.config(text=ip or "0.0.0.0")
        self._save_state()

    def _copy_share_ip(self):
        ip = self._share_ip_lbl.cget("text")
        if ip and ip != "0.0.0.0":
            self.clipboard_clear()
            self.clipboard_append(ip)
            self._flash_name_status(self._t("copied"))

    def _flash_name_status(self, msg: str, is_error=False):
        self._name_status_lbl.config(text=msg, fg=RED_PRIMARY if is_error else GREEN_SUCCESS)
        self.after(4000, lambda: self._name_status_lbl.config(text=""))

    def _on_save_player_name(self):
        name = self._player_var.get().strip()
        host_target = "127.0.0.1"
        if self._mode_var.get() == "join":
            host_target = self._join_host_var.get().strip() or "127.0.0.1"

        ok, msg = send_player_rename(name, host_target)
        self._flash_name_status(msg, is_error=(not ok))
        if ok:
            self.cfg["player_name"] = name
            self._save_state()

    def _browse_game(self):
        path = filedialog.askopenfilename(
            parent=self, title="NFS Most Wanted Executable",
            filetypes=[("NFS Executables", "NFS13.online.exe NFS13.exe"), ("All Executables", "*.exe")]
        )
        if path:
            self._game_path_var.set(path)
            self._save_state()

    def _do_patch(self):
        src = filedialog.askopenfilename(
            parent=self, title="Select NFS13.exe",
            filetypes=[("NFS13.exe", "NFS13.exe"), ("Executables", "*.exe")]
        )
        if not src:
            return

        ok, msg, out_path = apply_nfs13_patch(Path(src))
        if ok:
            if out_path:
                self._game_path_var.set(str(out_path))
                self._save_state()
            messagebox.showinfo("NFS13.online.exe", msg, parent=self)
        else:
            messagebox.showerror("Patcher Error", msg, parent=self)

    def _configure_firewall_native(self):
        ok, err = setup_windows_firewall()
        if ok:
            messagebox.showinfo("Firewall", self._t("firewall_ok"), parent=self)
        else:
            messagebox.showerror("Firewall", self._t("firewall_err").format(err), parent=self)

    def _save_state(self):
        """Persist current state to launcher.ini."""
        self.cfg["player_name"] = self._player_var.get().strip()
        self.cfg["game_path"]   = self._game_path_var.get().strip()
        self.cfg["mode"]        = self._mode_var.get()
        self.cfg["host_ip"]     = self._extract_ip(self._host_ip_var.get())
        self.cfg["join_ip"]     = self._join_host_var.get().strip()
        self.cfg["my_ip"]       = self._extract_ip(self._join_my_ip_var.get())
        if hasattr(self, "_speedlist_var"):
            sl_key = self._get_speedlist_key_from_label(self._speedlist_var.get())
            self.cfg["speedlist_mode"] = sl_key
            save_speedlist_mode_json(sl_key)
        self.cfg["language"]    = self.lang
        save_config(self.cfg)

    # ─────────────────────── Launch Flow ─────────────────────────────────────

    def _on_launch_clicked(self):
        self._save_state()
        mode = self._mode_var.get()

        # 1. Validate game executable
        game_path = self.cfg.get("game_path", "")
        if not game_path or not Path(game_path).exists():
            messagebox.showwarning("Game Path", self._t("game_path_missing"), parent=self)
            return

        # 2. Determine target IP for hosts redirection
        if mode == "host":
            target_ip = self.cfg.get("host_ip") or "127.0.0.1"
        else:
            target_ip = self.cfg.get("join_ip", "").strip()
            if not target_ip:
                messagebox.showwarning("Host IP", self._t("friend_ip_missing"), parent=self)
                return

        # 3. Update hosts file
        err = update_hosts_file(target_ip)
        if err:
            messagebox.showerror(self._t("hosts_err_title"), self._t("hosts_err_msg").format(err), parent=self)
            return

        # 4. If mode is HOST, ensure firewall, speedlist mode and start server
        if mode == "host":
            setup_windows_firewall()
            save_speedlist_mode_json(self.cfg.get("speedlist_mode", "all_races"))
            self._start_server(target_ip)

        # 5. Apply player name
        player_name = self.cfg.get("player_name", "Player1")
        send_player_rename(player_name, target_ip)

        # 6. Launch Game Executable
        try:
            gp = Path(game_path)
            game_proc = subprocess.Popen([str(gp)], cwd=str(gp.parent))
            self._flash_name_status("✓ Game launched!")

            def watch_game():
                try:
                    game_proc.wait()
                    # Clean up hosts when game closes
                    remove_hosts_entries()
                except Exception:
                    pass
            threading.Thread(target=watch_game, daemon=True).start()
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to launch game:\n{exc}", parent=self)

    def _start_server(self, ip: str):
        if self._server_proc and self._server_proc.poll() is None:
            return  # Server already active

        try:
            env = os.environ.copy()
            env["NFS13_HOST"] = ip
            env["NFS13_SPEEDLIST_MODE"] = self.cfg.get("speedlist_mode", "all_races")

            if getattr(sys, "frozen", False):
                # Embedded server in NFSMW_Launcher.exe
                cmd = ["cmd.exe", "/k", str(sys.executable), "--server", ip]
            elif SERVER_BAT.exists():
                cmd = ["cmd.exe", "/k", str(SERVER_BAT), ip]
            else:
                py_exe = find_python()
                cmd = ["cmd.exe", "/k", py_exe, str(SERVER_SCRIPT), ip]

            self._server_proc = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(BASE_DIR),
                env=env
            )
            self._srv_status_pill.config(text=f"● {self._t('server_on')} ({ip})", bg=GREEN_BG, fg=GREEN_SUCCESS)
            self._stop_srv_btn.pack(side="left", padx=(0, 8))
        except Exception as exc:
            messagebox.showerror("Server Error", f"Failed to start server:\n{exc}", parent=self)

    def _stop_server(self):
        if self._server_proc:
            try:
                self._server_proc.terminate()
            except Exception:
                pass
            self._server_proc = None
        self._srv_status_pill.config(text=self._t("server_off"), bg="#F1F3F6", fg=TEXT_MUTED)
        self._stop_srv_btn.pack_forget()

    def _clean_hosts(self):
        if messagebox.askyesno("Hosts", self._t("clean_hosts_confirm"), parent=self):
            err = remove_hosts_entries()
            if err:
                messagebox.showerror("Error", err, parent=self)
            else:
                messagebox.showinfo("Hosts", self._t("clean_hosts_ok"), parent=self)

    def _on_close(self):
        self._save_state()
        if self._server_proc and self._server_proc.poll() is None:
            if messagebox.askyesno("Server", self._t("stop_srv_confirm"), parent=self):
                self._stop_server()
        self.destroy()


def run_server_cli(target_ip: str = ""):
    """Runs the server backend in console mode when invoked with --server."""
    if getattr(sys, "frozen", False):
        import ctypes
        if not ctypes.windll.kernel32.AttachConsole(0xFFFFFFFF):
            ctypes.windll.kernel32.AllocConsole()
        try:
            sys.stdout = open("CONOUT$", "w", encoding="utf-8", buffering=1)
            sys.stderr = open("CONOUT$", "w", encoding="utf-8", buffering=1)
            sys.stdin = open("CONIN$", "r", encoding="utf-8")
        except Exception:
            pass
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("Need for Speed: Most Wanted (2012) - Server")
        except Exception:
            pass

    try:
        try:
            import run_server
            server_main = run_server.main
        except ImportError:
            import run_server_windows
            server_main = run_server_windows.main
        if target_ip:
            sys.argv = [sys.argv[0], target_ip]
        else:
            sys.argv = [sys.argv[0]]
        server_main()
    except Exception as exc:
        print(f"\n[ERROR] Server execution error: {exc}")
        import traceback
        traceback.print_exc()
        try:
            input("\nPress ENTER to exit...")
        except Exception:
            pass


# ─────────────────────────── Entry Point ─────────────────────────────────────

def main():
    if "--server" in sys.argv:
        idx = sys.argv.index("--server")
        target_ip = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        run_server_cli(target_ip)
        return

    if not is_admin():
        root = tk.Tk()
        root.withdraw()
        ans = messagebox.askyesno(
            "Administrator Rights Required",
            "This Launcher needs Administrator rights to manage the Windows hosts file.\n\nRestart as Administrator?",
            icon="warning"
        )
        root.destroy()
        if ans:
            relaunch_as_admin()
            sys.exit(0)

    app = NFSMWLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()
