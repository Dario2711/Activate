from flask import Blueprint, render_template, redirect, url_for, session, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.data.models.db_models import Usuario, Recompensa, CanjeRecompensa
from app.data.database import db
import os
from uuid import uuid4

import random

RECOMPENSAS_MOCKS = [
    {
        "nombre": "10% OFF en tienda Samsung",
        "descripcion": "Cupón exclusivo para usar en la tienda online de Samsung.",
        "puntos": 250,
        "imagen": "default.png"
    },
    {
        "nombre": "Auriculares Galaxy Buds",
        "descripcion": "Descuento para adquirir Galaxy Buds originales.",
        "puntos": 500,
        "imagen": "default.png"
    },
  {
        "nombre": "Reloj Galaxy Watch",
        "descripcion": "Participá del sorteo mensual por un smartwatch Galaxy.",
        "puntos": 650,
        "imagen": "default.png"
    },
    {
        "nombre": "Entrenamiento personalizado",
        "descripcion": "Sesión virtual con entrenador partner.",
        "puntos": 200,
        "imagen": "default.png"
    },
    {
        "nombre": "Gift Card PedidosYa",
        "descripcion": "Tarjeta regalo digital para delivery.",
        "puntos": 150,
        "imagen": "default.png"
    },
    {
        "nombre": "Sticker y Merch Activate",
        "descripcion": "Merchandising oficial del programa Activate.",
        "puntos": 50,
        "imagen": "default.png"
    }
]

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

# Landing secundarias
@main_bp.route('/como-funciona')
def como_funciona():
    return render_template('como_funciona.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            session['user_id'] = usuario.id
            session['es_admin'] = usuario.es_admin
            return redirect(url_for('main.index'))
        
        flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@main_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmar = request.form.get('confirmar_password', '')
        codigo_admin = request.form.get('codigo_admin', '')
        
        if not all([nombre, email, password]):
            flash('Completa todos los campos requeridos', 'danger')
            return render_template('registro.html')
        
        if password != confirmar:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('registro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email ya está registrado', 'danger')
            return render_template('registro.html')
        
        nuevo = Usuario(
            nombre=nombre,
            email=email,
            password=generate_password_hash(password),
            es_admin=(codigo_admin == '6767')
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('¡Registro exitoso! Ya podés iniciar sesión', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('registro.html')

@main_bp.route('/juego')
def juego():
    if 'user_id' not in session:
        flash('Iniciá sesión para jugar', 'warning')
        return redirect(url_for('main.login'))
    
    top_usuarios = Usuario.query.filter_by(es_admin=False).order_by(Usuario.puntaje_maximo.desc()).limit(10).all()
    return render_template('juego.html', top_usuarios=top_usuarios)

# Recompensas vista/canjeo
@main_bp.route('/recompensas', methods=['GET', 'POST'])
def recompensas():
    if 'user_id' not in session:
        flash('Iniciá sesión para acceder a recompensas', 'warning')
        return redirect(url_for('main.login'))

    usuario = Usuario.query.get(session['user_id'])
    # Inicializar recompensas de base sólo si no hay ninguna
    if not Recompensa.query.first():
        for data in RECOMPENSAS_MOCKS:
            recompensa = Recompensa(**data)
            db.session.add(recompensa)
        db.session.commit()

    recompensas = Recompensa.query.all()

    if request.method == 'POST':
        rid = request.form.get('recompensa_id')
        recompensa = Recompensa.query.get(rid)
        if not recompensa:
            flash('Recompensa no encontrada', 'danger')
            return redirect(url_for('main.recompensas'))
        if usuario.puntaje_maximo < recompensa.puntos:
            flash('No tenés suficientes puntos para canjear esta recompensa', 'warning')
            return redirect(url_for('main.recompensas'))
        c = CanjeRecompensa(usuario_id=usuario.id, recompensa_id=recompensa.id)
        db.session.add(c)
        usuario.puntaje_maximo -= recompensa.puntos
        db.session.commit()
        flash(f'Recompensa canjeada: {recompensa.nombre}', 'success')
        return redirect(url_for('main.recompensas'))

    # Obtener logros (canjes) para mostrarlos en el modal opcionalmente
    logros = CanjeRecompensa.query.filter_by(usuario_id=usuario.id).order_by(CanjeRecompensa.fecha.desc()).all()
    return render_template('recompensas.html', usuario=usuario, recompensas=recompensas, logros=logros)

# Mostrar logros/canjes en perfil
def get_logros(usuario_id):
    return CanjeRecompensa.query.filter_by(usuario_id=usuario_id).order_by(CanjeRecompensa.fecha.desc()).all()

# Ajustar ruta de perfil para incluir logros
@main_bp.route('/perfil')
def perfil():
    if 'user_id' not in session:
        flash('Iniciá sesión para ver tu perfil', 'danger')
        return redirect(url_for('main.login'))
    usuario = Usuario.query.get(session['user_id'])
    logros = get_logros(usuario.id)
    return render_template('perfil.html', usuario=usuario, logros=logros)

@main_bp.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        flash('Iniciá sesión para editar tu perfil', 'danger')
        return redirect(url_for('main.login'))

    usuario = Usuario.query.get(session['user_id'])
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        biografia = request.form.get('biografia', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if nombre:
            usuario.nombre = nombre
        if email:
            usuario.email = email
        usuario.biografia = biografia

        if password:
            if password != confirm_password or len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres y coincidir', 'danger')
                return render_template('editar_perfil.html', usuario=usuario)
            usuario.password = generate_password_hash(password)

        archivo = request.files.get('foto_perfil')
        if archivo and archivo.filename:
            ext = archivo.filename.rsplit('.', 1)[-1].lower() if '.' in archivo.filename else ''
            formatos_permitidos = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
            
            if ext not in formatos_permitidos:
                flash('Formato de imagen no permitido', 'danger')
                return render_template('editar_perfil.html', usuario=usuario)
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_folder, exist_ok=True)
            
            filename = secure_filename(f"{usuario.id}_{uuid4().hex}.{ext}")
            ruta = os.path.join(upload_folder, filename)
            archivo.save(ruta)

            if usuario.foto_perfil and usuario.foto_perfil != 'default.svg':
                foto_antigua = os.path.join(upload_folder, usuario.foto_perfil)
                if os.path.exists(foto_antigua):
                    try:
                        os.remove(foto_antigua)
                    except:
                        pass

            usuario.foto_perfil = filename

        db.session.commit()
        flash('Perfil actualizado', 'success')
        return redirect(url_for('main.perfil'))

    return render_template('editar_perfil.html', usuario=usuario)

@main_bp.route('/ranking')
def ranking():
    top_usuarios = Usuario.query.filter_by(es_admin=False).order_by(Usuario.puntaje_maximo.desc()).limit(10).all()
    return render_template('ranking.html', top_usuarios=top_usuarios)

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Iniciá sesión para acceder al panel', 'danger')
        return redirect(url_for('main.login'))

    actual = Usuario.query.get(session['user_id'])
    if not actual or not actual.es_admin:
        flash('No tenés permisos de administrador', 'danger')
        return redirect(url_for('main.index'))

    usuarios = Usuario.query.order_by(Usuario.id.asc()).all()
    return render_template('admin/dashboard.html', usuarios=usuarios)

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('main.index'))
