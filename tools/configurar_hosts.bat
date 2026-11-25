@echo off
chcp 65001 >nul
title Configurar Archivo Hosts para NFSMW12

openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Este script requiere permisos de Administrador.
    echo Haz clic derecho sobre este archivo y selecciona "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

echo =======================================================================
echo     REDIRECCION DNS (HOSTS) PARA SERVIDOR NFSMW12
echo =======================================================================
echo.
set /p SERVER_IP="Ingresa la IP del Servidor LAN o Radmin (ej: 26.x.x.x o 192.168.x.x): "

if "%SERVER_IP%"=="" (
    echo [ERROR] No se especifico ninguna IP. Operacion cancelada.
    pause
    exit /b 1
)

set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts

:: Limpiar entradas previas
powershell -Command "$content = Get-Content '%HOSTS_FILE%' | Where-Object { $_ -notmatch 'ea\.com' -or $_ -notmatch 'gosredirector|nfs13-pc|demangler|peach' }; Set-Content '%HOSTS_FILE%' $content"

:: Agregar nuevas entradas
echo. >> "%HOSTS_FILE%"
echo # NFSMW12 LAN Server >> "%HOSTS_FILE%"
echo %SERVER_IP% gosredirector.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% gosredirector.online.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% gosredirector.scert.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% gosredirector.stest.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% gosca.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% nfs13-pc.blaze.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% demangler.ea.com >> "%HOSTS_FILE%"
echo %SERVER_IP% peach.online.ea.com >> "%HOSTS_FILE%"

echo.
echo =======================================================================
echo [OK] Archivo hosts actualizado apuntando a %SERVER_IP%!
echo =======================================================================
echo.
pause
