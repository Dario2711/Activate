import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///usuarios.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # La app sirve estáticos desde app/presentation/web/static
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'presentation', 'web', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def init_app(app):
        # Crear carpeta de subidas si no existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
