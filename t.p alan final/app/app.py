from flask import Flask
from functools import wraps
import os

from app.core.config.settings import Config
from app.data.database import db, init_db
from app.data.models.db_models import Usuario
from app.presentation.api.routes import api_bp
from app.presentation.routes import main_bp

def create_app(config_class=Config):
    base_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(base_dir, 'presentation', 'web', 'templates')
    static_dir = os.path.join(base_dir, 'presentation', 'web', 'static')
    
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    init_db(app)
    config_class.init_app(app)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.context_processor
    def inject_user():
        from flask import session
        if 'user_id' in session:
            usuario = Usuario.query.get(session['user_id'])
            return dict(usuario=usuario)
        return dict(usuario=None)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
