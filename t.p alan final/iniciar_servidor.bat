@echo off
setlocal enabledelayedexpansion

title Servidor del Juego de Escritura Rápida
color 0A

echo ===========================================
echo    Iniciando el servidor del juego...
echo ===========================================
echo.

:: Configurar el entorno
set FLASK_APP=app/app.py
set FLASK_DEBUG=1
set PYTHONPATH=%~dp0

:: Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo.
    echo Por favor, instala Python 3.6 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrate de marcar la opción "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

:: Verificar e instalar dependencias
echo [*] Verificando e instalando dependencias...
python -m pip install --upgrade pip >nul 2>&1

:: Verificar si requirements.txt existe
if not exist "requirements.txt" (
    echo [*] Creando archivo requirements.txt...
    (
        echo Flask==2.3.3
        echo Flask-SQLAlchemy==3.1.1
        echo Werkzeug==2.3.7
        echo python-dotenv==1.0.0
    ) > requirements.txt
)

echo [*] Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias automáticamente.
    echo Intentando instalar manualmente...
    pip install flask flask-sqlalchemy werkzeug python-dotenv
    
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudieron instalar las dependencias.
        echo Por favor, ejecuta manualmente: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [*] Dependencias verificadas correctamente.
echo.

:: Detener cualquier instancia previa
echo [*] Deteniendo servidores previos...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

:: Iniciar servicios (TCP y luego Flask)
echo ===========================================
echo [*] Iniciando servicios...
echo [*] Servidor de persistencia TCP: 127.0.0.1:6000
echo [*] Backend Flask: http://127.0.0.1:5000
echo ===========================================
echo.

:: Iniciar servidor TCP de persistencia en otra ventana
start "TCP Persistence Server" cmd /c python "app\infrastructure\tcp_server.py"
timeout /t 1 >nul

echo.
echo [i] El servidor se ha detenido.
pause
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo.
    echo Por favor, instala Python 3.6 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrate de marcar la opción "Add Python to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)

echo [✓] Python está correctamente instalado.
echo.

:: Verificar e instalar dependencias
echo Verificando dependencias...
echo.

for %%p in (flask flask-sqlalchemy) do (
    python -c "import %%p" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo [i] Instalando %%p...
        pip install %%p --quiet
        if !ERRORLEVEL! NEQ 0 (
            echo [ERROR] No se pudo instalar %%p. Intenta ejecutar 'pip install %%p' manualmente.
            pause
            exit /b 1
        )
    )
)

echo.
echo [✓] Todas las dependencias están instaladas.
echo.

:: Crear directorio de instancia si no existe
if not exist "instance" (
    echo [i] Creando directorio 'instance'...
    mkdir instance
)

:: Crear la base de datos si no existe (usando create_app)
python -c "from app.app import create_app; from app.data.database import db; app=create_app(); app.app_context().push(); db.create_all()"

:start_server
cls
echo ===========================================
echo    SERVIDOR DEL JUEGO DE ESCRITURA RÁPIDA
echo ===========================================
echo.
echo [i] Iniciando el servidor...
echo [i] URL: http://localhost:5000
echo [i] Presiona Ctrl+C para detener el servidor
echo.
echo ===========================================
echo.

:: Iniciar el servidor Flask con FLASK_APP (evitar PATH usando python -m)
python -m flask run --host=0.0.0.0 --port=5000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar el servidor.
    echo.
    echo Posibles causas:
    echo 1. El puerto 5000 está en uso por otra aplicación
    echo 2. Hay un error en el código de la aplicación
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
    exit /b 1
)

echo.
echo [i] El servidor se ha detenido.
echo.

choice /c SN /m "¿Deseas reiniciar el servidor? (S/N): "
if %ERRORLEVEL% == 1 (
    goto start_server
)

echo.
echo [i] Saliendo...
timeout /t 3 >nul
