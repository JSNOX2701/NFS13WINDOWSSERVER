@echo off
chcp 65001 >nul
title Servidor Need for Speed Most Wanted (2012) - LAN Windows

echo =======================================================================
echo     SERVIDOR NFSMW 2012 - MODO LAN NATIVO PARA WINDOWS
echo =======================================================================
echo.

if not "%~1"=="" (
    set HOST_IP=%~1
) else (
    set /p HOST_IP="Ingresa tu IP de Radmin VPN o LAN (o ENTER para auto-detectar): "
)

if exist "%~dp0NFSMW_Launcher.exe" (
    if "%HOST_IP%"=="" (
        "%~dp0NFSMW_Launcher.exe" --server
    ) else (
        "%~dp0NFSMW_Launcher.exe" --server %HOST_IP%
    )
    exit /b 0
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se detecto Python instalado ni NFSMW_Launcher.exe.
    echo Por favor instala Python o ejecuta NFSMW_Launcher.exe.
    echo.
    pause
    exit /b 1
)

python -c "import tlslite" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Instalando tlslite-ng para emulacion SSLv3 en Windows...
    python -m pip install tlslite-ng
    echo.
)

if "%HOST_IP%"=="" (
    python "%~dp0run_server.py"
) else (
    python "%~dp0run_server.py" %HOST_IP%
)

pause
