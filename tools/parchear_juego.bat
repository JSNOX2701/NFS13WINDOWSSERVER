@echo off
chcp 65001 >nul
title Parchear NFS13.exe para Servidor LAN

echo =======================================================================
echo     PARCHEADOR AUTOMATICO DE CLIENTE - NEED FOR SPEED MOST WANTED 2012
echo =======================================================================
echo.

set "ROOT_DIR=%~dp0..\"
if exist "%~dp0client\patch_nfs13.py" (
    set "ROOT_DIR=%~dp0"
)

set EXE_PATH=%1

if "%EXE_PATH%"=="" (
    echo Puedes arrastrar el archivo NFS13.exe sobre este archivo bat, o
    set /p EXE_PATH="Pega o escribe la ruta completa hacia tu NFS13.exe: "
)

set EXE_PATH=%EXE_PATH:"=%

if not exist "%EXE_PATH%" (
    echo.
    echo [ERROR] No se encontro el archivo: "%EXE_PATH%"
    echo.
    pause
    exit /b 1
)

echo.
echo [+] Aplicando parche a "%EXE_PATH%"...
python "%ROOT_DIR%client\patch_nfs13.py" "%EXE_PATH%"

echo.
pause
