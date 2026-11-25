# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for NFS Most Wanted 2012 Private Server Launcher
from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = [
    ('client/patch_nfs13.py', 'client'),
    ('client/patches', 'client/patches'),
    ('client/hosts.txt', 'client'),
    ('server', 'server'),
    ('certs', 'certs'),
    ('run_server.py', '.'),
    ('icon.ico', '.'),
]

tls_datas, tls_binaries, tls_hidden = collect_all('tlslite')
datas += tls_datas

hiddenimports = [
    'ctypes',
    'ctypes.windll',
    'configparser',
    'threading',
    'urllib.parse',
    'urllib.request',
    'urllib.error',
    'json',
    'socket',
    'subprocess',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'asyncio',
    'asyncio.runners',
    'server',
    'server.server',
    'server.ssl_proxy',
    'run_server',
] + tls_hidden

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=tls_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nfsmw_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    uac_admin=True,
    uac_uiaccess=False,
    icon='icon.ico',
)
