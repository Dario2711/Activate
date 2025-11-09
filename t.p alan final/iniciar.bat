@echo off
title Activate - Sistema Completo
color 0A

echo ========================================
echo    ACTIVATE - Iniciando Sistema
echo ========================================
echo.

cd /d "%~dp0"

:: Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no esta instalado
    echo Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] Verificando dependencias...
if not exist "requirements.txt" (
    echo Flask==2.3.3 > requirements.txt
    echo Flask-SQLAlchemy==3.1.1 >> requirements.txt
    echo Werkzeug==2.3.7 >> requirements.txt
    echo python-dotenv==1.0.0 >> requirements.txt
)

pip install -q -r requirements.txt >nul 2>&1

echo [*] Iniciando servicios...
echo.

:: Iniciar TCP Server
echo [1/3] Servidor TCP (Puerto 6000)...
start "TCP Server" cmd /k "cd /d %~dp0 && python -m app.infrastructure.tcp_server"
timeout /t 2 /nobreak >nul

:: Iniciar Distributed Service
echo [2/3] Servicio Distribuido (Puerto 7000)...
start "Distributed Service" cmd /k "cd /d %~dp0 && python -m app.infrastructure.distributed_service"
timeout /t 2 /nobreak >nul

:: Iniciar Flask Server
echo [3/3] Servidor Flask (Puerto 5000)...
start "Flask Server" cmd /k "cd /d %~dp0 && python -m app"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    Sistema iniciado correctamente
echo ========================================
echo.
echo Servicios activos:
echo   - TCP Server: localhost:6000
echo   - Distributed Service: localhost:7000
echo   - Web App: http://localhost:5000
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul

