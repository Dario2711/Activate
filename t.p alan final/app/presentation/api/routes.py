from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from flask import current_app as app
from app.data.models.db_models import Usuario
from app.data.database import db
from functools import wraps
from datetime import datetime
from app.infrastructure.tcp_client import save_score_via_tcp

api_bp = Blueprint('api', __name__)

# Decorador local basado en sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Para API devolvemos 401 JSON en lugar de redirigir
            if request.is_json:
                return jsonify({'success': False, 'error': 'No autenticado'}), 401
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta para guardar puntaje
@api_bp.route('/guardar_puntaje', methods=['POST'])
@login_required
def guardar_puntaje():
    try:
        data = request.get_json()
        if not data or 'puntaje' not in data:
            return jsonify({'success': False, 'error': 'Puntaje no proporcionado'}), 400
            
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.es_admin:
            return jsonify({'success': False, 'error': 'Usuario no encontrado o no autorizado'}), 404
        
        puntaje = int(data['puntaje'])
        if puntaje > usuario.puntaje_maximo:
            usuario.puntaje_maximo = puntaje
            usuario.fecha_ultimo_juego = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': '¡Nuevo récord!',
                'nuevo_record': True,
                'puntaje_maximo': usuario.puntaje_maximo
            })
        else:
            return jsonify({
                'success': True, 
                'message': 'Puntaje guardado',
                'nuevo_record': False,
                'puntaje_maximo': usuario.puntaje_maximo
            })
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error en guardar_puntaje: {str(e)}')
        return jsonify({'success': False, 'error': 'Error al procesar el puntaje'}), 500

# Ruta para reiniciar puntuación
@api_bp.route('/admin/reiniciar_puntuacion/<int:usuario_id>', methods=['POST'])
@login_required
def reiniciar_puntaje(usuario_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
        
    # Verificar si el usuario actual es administrador
    usuario_actual = Usuario.query.get(session['user_id'])
    if not usuario_actual or not usuario_actual.es_admin:
        flash('No tienes permiso para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    # Buscar al usuario objetivo
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    try:
        usuario.puntaje_maximo = 0
        db.session.commit()
        flash(f'Puntuación de {usuario.nombre} reiniciada correctamente', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al reiniciar la puntuación', 'danger')
    return redirect(url_for('main.admin_dashboard'))

# Ruta alternativa que usa el servidor de persistencia TCP para guardar puntaje
@api_bp.route('/guardar_puntaje_tcp', methods=['POST'])
@login_required
def guardar_puntaje_tcp():
    try:
        data = request.get_json()
        if not data or 'puntaje' not in data:
            return jsonify({'success': False, 'error': 'Puntaje no proporcionado'}), 400

        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.es_admin:
            return jsonify({'success': False, 'error': 'Usuario no encontrado o no autorizado'}), 404

        puntaje = int(data['puntaje'])
        ok, resp = save_score_via_tcp(usuario.id, puntaje)
        status = 200 if ok else 500
        return jsonify(resp), status
    except Exception as e:
        app.logger.error(f'Error en guardar_puntaje_tcp: {str(e)}')
        return jsonify({'success': False, 'error': 'Error al procesar el puntaje por TCP'}), 500

# Eliminar usuario (solo admin)
@api_bp.route('/admin/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    # Debe haber un admin logueado
    admin_actual = Usuario.query.get(session['user_id'])
    if not admin_actual or not admin_actual.es_admin:
        flash('No tienes permiso para realizar esta acción', 'danger')
        return redirect(url_for('main.index'))

    # No permitir que un admin elimine su propio usuario desde aquí
    if admin_actual.id == usuario_id:
        flash('No puedes eliminar tu propia cuenta desde el panel.', 'warning')
        return redirect(url_for('main.admin_dashboard'))

    # Validar contraseña de admin desde el formulario
    admin_password = request.form.get('admin_password', '')
    # Aceptar la contraseña del admin o el código maestro 6767 (usado en registro)
    if not admin_password or (admin_password != '6767' and not admin_actual.check_password(admin_password)):
        flash('Contraseña de administrador incorrecta.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado correctamente', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar el usuario', 'danger')
    return redirect(url_for('main.admin_dashboard'))
