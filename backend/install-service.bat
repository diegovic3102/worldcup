@echo off
REM ============================================================
REM  Registra el backend de sucesores-worldcup como servicio
REM  de Windows (NSSM), independiente y con arranque automatico.
REM  EJECUTAR COMO ADMINISTRADOR (clic derecho -> Ejecutar como
REM  administrador). Solo se corre una vez.
REM ============================================================

set SERVICE=sucesores-worldcup-api
set PYTHON=C:\Users\dappcalidad\AppData\Local\Programs\Python\Python312\python.exe
set APPDIR=D:\Projects\sucesores-worldcup\backend
set SCRIPT=%APPDIR%\serve.py

echo.
echo === 1) Liberando el puerto 5001 (proceso manual de flask, si existe) ===
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001 " ^| findstr "LISTENING"') do (
    echo Deteniendo PID %%a que ocupa el 5001...
    taskkill /F /PID %%a
)

echo.
echo === 2) Quitando servicio previo con el mismo nombre (si existe) ===
nssm stop %SERVICE% 2>nul
nssm remove %SERVICE% confirm 2>nul

echo.
echo === 3) Instalando el servicio ===
nssm install %SERVICE% "%PYTHON%" "%SCRIPT%"
nssm set %SERVICE% AppDirectory "%APPDIR%"
nssm set %SERVICE% DisplayName "Sucesores Worldcup API"
nssm set %SERVICE% Description "Backend Flask (waitress) de la polla mundialista, puerto 5001"
nssm set %SERVICE% Start SERVICE_AUTO_START
nssm set %SERVICE% AppStdout "%APPDIR%\service.out.log"
nssm set %SERVICE% AppStderr "%APPDIR%\service.err.log"
nssm set %SERVICE% AppExit Default Restart
nssm set %SERVICE% AppRestartDelay 3000

echo.
echo === 4) Iniciando el servicio ===
nssm start %SERVICE%

echo.
echo === Estado ===
sc query %SERVICE% | findstr STATE

echo.
echo Listo. El backend ahora arranca solo al reiniciar Windows.
echo Para ver su estado:   sc query %SERVICE%
echo Para detenerlo:       nssm stop %SERVICE%
echo Para quitarlo:        nssm remove %SERVICE% confirm
echo.
pause