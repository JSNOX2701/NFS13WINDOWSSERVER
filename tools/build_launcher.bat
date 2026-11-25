@echo off
setlocal
cd /d "%~dp0\.."

echo =======================================================================
echo    COMPILANDO LAN LAUNCHER PARA NEED FOR SPEED: MOST WANTED (2012)
echo =======================================================================
echo.

python -m PyInstaller launcher.spec --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la compilacion con PyInstaller.
    pause
    exit /b 1
)

if exist dist\nfsmw_launcher.exe (
    copy /y dist\nfsmw_launcher.exe NFSMW_Launcher.exe >nul
    echo.
    echo [EXITO] Ejecutable generado correctamente: NFSMW_Launcher.exe
) else (
    echo.
    echo [ERROR] No se encontro dist\nfsmw_launcher.exe
)

echo.
pause
