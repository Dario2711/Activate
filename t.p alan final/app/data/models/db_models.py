from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.data.database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    puntaje_maximo = db.Column(db.Integer, default=0)
    fecha_ultimo_juego = db.Column(db.DateTime, nullable=True)
    foto_perfil = db.Column(db.String(200), default='default.svg')
    biografia = db.Column(db.Text, default='')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Usuario {self.email}>'
