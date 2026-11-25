@echo off
setlocal
cd /d "%~dp0\.."

echo =======================================================================
echo    SIMULADOR DE SEGUNDO JUGADOR (GHOSTRIVAL) - NFS MOST WANTED 2012
echo =======================================================================
echo.
echo  1. Primero inicia tu servidor y juego con "HOST AND PLAY".
echo  2. Entra al modo Multijugador / crea una partida de amigos o publica.
echo  3. Este bot entrara desde 127.0.0.2 como un segundo jugador real para
echo     verificar que tu juego NO crashee al recibir al segundo jugador.
echo.

python tools\simular_jugador2.py %*
echo.
pause
