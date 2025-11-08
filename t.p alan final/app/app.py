from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os

# Importar configuración
from app.core.config.settings import Config
from app.data.database import db, init_db

# Importar modelos
from app.data.models.db_models import Usuario

# Importar rutas
from app.presentation.api.routes import api_bp
from app.presentation.routes import main_bp

def create_app(config_class=Config):
    base_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(base_dir, 'presentation', 'web', 'templates')
    static_dir = os.path.join(base_dir, 'presentation', 'web', 'static')
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Inicializar base de datos
    init_db(app)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Inicializar configuración
    config_class.init_app(app)
    
    # Contexto de procesamiento para el usuario actual
    @app.context_processor
    def inject_user():
        if 'user_id' in session:
            usuario = Usuario.query.get(session['user_id'])
            return dict(usuario=usuario)
        return dict(usuario=None)
    
    # Funciones de utilidad
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
    
    # Decorador para requerir inicio de sesión
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor inicia sesión para acceder a esta página.', 'danger')
                return redirect(url_for('main.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Decorador para requerir ser administrador
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor inicia sesión como administrador.', 'danger')
                return redirect(url_for('main.login'))
            
            usuario = Usuario.query.get(session['user_id'])
            if not usuario or not usuario.es_admin:
                flash('No tienes permisos de administrador.', 'danger')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    
    # Las rutas están siendo importadas a través de los blueprints
    # No es necesario importar routes aquí
    
    return app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
