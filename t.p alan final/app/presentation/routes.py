from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from app.data.models.db_models import Usuario
from app.data.database import db
import os
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import current_app

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
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not check_password_hash(usuario.password, password):
            flash('Email o contraseña incorrectos', 'danger')
            return render_template('login.html')
        session['user_id'] = usuario.id
        session['es_admin'] = usuario.es_admin
        return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmar = request.form.get('confirmar_password')
        codigo_admin = request.form.get('codigo_admin')
        if not nombre or not email or not password:
            flash('Completa todos los campos requeridos', 'danger')
            return render_template('registro.html')
        if password != confirmar:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('registro.html')
        if Usuario.query.filter_by(email=email).first():
            flash('Este email ya está registrado', 'danger')
            return render_template('registro.html')
        es_admin = True if codigo_admin == '6767' else False
        nuevo = Usuario(
            nombre=nombre,
            email=email,
            password=generate_password_hash(password),
            es_admin=es_admin
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('main.login'))
    return render_template('registro.html')

@main_bp.route('/juego')
def juego():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para jugar.', 'warning')
        return redirect(url_for('main.login'))
    top_usuarios = Usuario.query.order_by(Usuario.puntaje_maximo.desc()).limit(10).all()
    return render_template('juego.html', top_usuarios=top_usuarios)

@main_bp.route('/perfil')
def perfil():
    return render_template('perfil.html')

@main_bp.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para editar tu perfil.', 'danger')
        return redirect(url_for('main.login'))

    usuario = Usuario.query.get(session['user_id'])
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        biografia = request.form.get('biografia')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if nombre:
            usuario.nombre = nombre
        if email:
            usuario.email = email
        if biografia is not None:
            usuario.biografia = biografia

        if password:
            if password == confirm_password and len(password) >= 6:
                usuario.password = generate_password_hash(password)
            else:
                flash('La contraseña no es válida o no coincide.', 'danger')
                return render_template('editar_perfil.html', usuario=usuario)

        archivo = request.files.get('foto_perfil')
        if archivo and archivo.filename:
            ext = archivo.filename.rsplit('.', 1)[-1].lower() if '.' in archivo.filename else ''
            if ext in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}:
                filename = secure_filename(f"{usuario.id}_{uuid4().hex}.{ext}")
                upload_folder = current_app.config.get('UPLOAD_FOLDER')
                os.makedirs(upload_folder, exist_ok=True)
                ruta = os.path.join(upload_folder, filename)
                archivo.save(ruta)

                if usuario.foto_perfil and usuario.foto_perfil != 'default.svg':
                    try:
                        antiguo = os.path.join(upload_folder, usuario.foto_perfil)
                        if os.path.exists(antiguo):
                            os.remove(antiguo)
                    except Exception:
                        pass

                usuario.foto_perfil = filename
            else:
                flash('Formato de imagen no permitido.', 'danger')
                return render_template('editar_perfil.html', usuario=usuario)

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('main.perfil'))

    return render_template('editar_perfil.html', usuario=usuario)

@main_bp.route('/ranking')
def ranking():
    top_usuarios = Usuario.query.filter_by(es_admin=False).order_by(Usuario.puntaje_maximo.desc()).limit(10).all()
    return render_template('ranking.html', top_usuarios=top_usuarios)

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para acceder al panel de administración.', 'danger')
        return redirect(url_for('main.login'))

    actual = Usuario.query.get(session['user_id'])
    if not actual or not actual.es_admin:
        flash('No tienes permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))

    usuarios = Usuario.query.order_by(Usuario.id.asc()).all()
    return render_template('admin/dashboard.html', usuarios=usuarios)

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('main.index'))
