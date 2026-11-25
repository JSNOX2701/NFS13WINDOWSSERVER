@echo off
cd /d "%~dp0\.."
echo =======================================================================
echo    ACTUALIZANDO LAUNCHER CON LAS 40 CARRERAS
echo =======================================================================
echo.
copy /y dist\nfsmw_launcher.exe NFSMW_Launcher.exe >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Por favor cierra el juego o el Launcher primero para poder reemplazar el archivo.
    echo.
) else (
    echo [EXITO] Launcher actualizado con las 40 carreras (Sprints y Circuitos).
    echo.
)
pause
