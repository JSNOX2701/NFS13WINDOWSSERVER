@echo off
chcp 65001 >nul
title Restaurar Archivo Hosts para NFSMW12

openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Este script requiere permisos de Administrador.
    echo Haz clic derecho sobre este archivo y selecciona "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

echo =======================================================================
echo     RESTAURANDO ARCHIVO HOSTS ORIGINAL...
echo =======================================================================
echo.

set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts

powershell -Command "$content = Get-Content '%HOSTS_FILE%' | Where-Object { $_ -notmatch 'ea\.com' -and $_ -notmatch 'NFSMW' -and $_ -notmatch 'gosredirector|nfs13-pc|demangler|peach' }; Set-Content '%HOSTS_FILE%' $content"

echo [OK] Redirecciones de EA eliminadas correctamente. Tu Windows esta limpio.
echo.
pause
