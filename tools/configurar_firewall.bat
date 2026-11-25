@echo off
chcp 65001 >nul
title Configurar Reglas de Firewall para NFSMW12 (LAN / Radmin)

:: Verificar permisos de Administrador
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Este script requiere permisos de Administrador.
    echo Haz clic derecho sobre este archivo y selecciona "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

echo =======================================================================
echo     Abriendo Puertos en el Firewall de Windows para NFSMW12...
echo =======================================================================
echo.

echo [+] Habilitando TCP 42127 (Blaze SSLv3)...
netsh advfirewall firewall add rule name="NFSMW12 - Blaze SSL" dir=in action=allow protocol=TCP localport=42127 profile=any >nul

echo [+] Habilitando TCP 44125 (HTTPS Redirect)...
netsh advfirewall firewall add rule name="NFSMW12 - HTTPS SSL" dir=in action=allow protocol=TCP localport=44125 profile=any >nul

echo [+] Habilitando TCP 8080 (Autolog HTTP)...
netsh advfirewall firewall add rule name="NFSMW12 - Autolog HTTP" dir=in action=allow protocol=TCP localport=8080 profile=any >nul

echo [+] Habilitando TCP/UDP 17500 (QoS Latencia)...
netsh advfirewall firewall add rule name="NFSMW12 - QoS TCP" dir=in action=allow protocol=TCP localport=17500 profile=any >nul
netsh advfirewall firewall add rule name="NFSMW12 - QoS UDP" dir=in action=allow protocol=UDP localport=17500 profile=any >nul

echo [+] Habilitando UDP 3659 (Carreras P2P entre Jugadores)...
netsh advfirewall firewall add rule name="NFSMW12 - P2P Mesh UDP" dir=in action=allow protocol=UDP localport=3659 profile=any >nul

echo.
echo =======================================================================
echo [OK] Todos los puertos fueron habilitados exitosamente en el Firewall!
echo =======================================================================
echo.
pause
