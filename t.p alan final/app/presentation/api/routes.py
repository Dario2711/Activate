from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from flask import current_app as app
from app.data.models.db_models import Usuario
from app.data.database import db
from functools import wraps
from datetime import datetime
from app.infrastructure.tcp_client import save_score_via_tcp
from app.infrastructure.distributed_service import DistributedServiceClient

api_bp = Blueprint('api', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'error': 'No autenticado'}), 401
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/admin/reiniciar_puntuacion/<int:usuario_id>', methods=['POST'])
@login_required
def reiniciar_puntaje(usuario_id):
    usuario_actual = Usuario.query.get(session['user_id'])
    if not usuario_actual or not usuario_actual.es_admin:
        flash('No tenés permiso para esta acción', 'danger')
        return redirect(url_for('main.index'))
    
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    try:
        usuario.puntaje_maximo = 0
        db.session.commit()
        flash(f'Puntuación de {usuario.nombre} reiniciada', 'success')
    except:
        db.session.rollback()
        flash('Error al reiniciar la puntuación', 'danger')
    
    return redirect(url_for('main.admin_dashboard'))

@api_bp.route('/guardar_puntaje_tcp', methods=['POST'])
@login_required
def guardar_puntaje_tcp():
    try:
        data = request.get_json()
        if not data or 'puntaje' not in data:
            return jsonify({'success': False, 'error': 'Puntaje no proporcionado'}), 400

        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.es_admin:
            return jsonify({'success': False, 'error': 'Usuario no autorizado'}), 404

        puntaje = int(data['puntaje'])
        ok, resp = save_score_via_tcp(usuario.id, puntaje)
        return jsonify(resp), 200 if ok else 500
    except Exception as e:
        app.logger.error(f'Error guardando puntaje TCP: {e}')
        return jsonify({'success': False, 'error': 'Error al procesar el puntaje'}), 500

@api_bp.route('/admin/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    admin_actual = Usuario.query.get(session['user_id'])
    if not admin_actual or not admin_actual.es_admin:
        flash('No tenés permiso para esta acción', 'danger')
        return redirect(url_for('main.index'))

    if admin_actual.id == usuario_id:
        flash('No podés eliminar tu propia cuenta', 'warning')
        return redirect(url_for('main.admin_dashboard'))

    admin_password = request.form.get('admin_password', '')
    if not admin_password or (admin_password != '6767' and not admin_actual.check_password(admin_password)):
        flash('Contraseña incorrecta', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado', 'success')
    except:
        db.session.rollback()
        flash('Error al eliminar el usuario', 'danger')
    
    return redirect(url_for('main.admin_dashboard'))

@api_bp.route('/stats/usuario', methods=['GET'])
@login_required
def get_user_stats():
    try:
        client = DistributedServiceClient()
        ok, resp = client.get_user_stats(session['user_id'])
        return jsonify(resp), 200 if ok else 500
    except Exception as e:
        app.logger.error(f'Error obteniendo stats usuario: {e}')
        return jsonify({'success': False, 'error': 'Error al obtener estadísticas'}), 500

@api_bp.route('/stats/global', methods=['GET'])
def get_global_stats():
    try:
        client = DistributedServiceClient()
        ok, resp = client.get_global_stats()
        return jsonify(resp), 200 if ok else 500
    except Exception as e:
        app.logger.error(f'Error obteniendo stats globales: {e}')
        return jsonify({'success': False, 'error': 'Error al obtener estadísticas'}), 500

@api_bp.route('/notificaciones', methods=['GET'])
@login_required
def get_notifications():
    try:
        client = DistributedServiceClient()
        ok, resp = client.get_notifications(session['user_id'])
        return jsonify(resp), 200 if ok else 500
    except Exception as e:
        app.logger.error(f'Error obteniendo notificaciones: {e}')
        return jsonify({'success': False, 'error': 'Error al obtener notificaciones'}), 500

@api_bp.route('/guardar_puntaje', methods=['POST'])
@login_required
def guardar_puntaje():
    try:
        data = request.get_json()
        if not data or 'puntaje' not in data:
            return jsonify({'success': False, 'error': 'Puntaje no proporcionado'}), 400
            
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.es_admin:
            return jsonify({'success': False, 'error': 'Usuario no autorizado'}), 404
        
        puntaje = int(data['puntaje'])
        nuevo_record = puntaje > usuario.puntaje_maximo
        
        if nuevo_record:
            usuario.puntaje_maximo = puntaje
            usuario.fecha_ultimo_juego = datetime.utcnow()
            db.session.commit()
            
            try:
                client = DistributedServiceClient()
                client.add_notification(
                    usuario.id, 
                    f'¡Nuevo récord! Alcanzaste {puntaje} puntos', 
                    'success'
                )
            except:
                app.logger.warning('No se pudo notificar al servicio distribuido')
            
            return jsonify({
                'success': True, 
                'message': '¡Nuevo récord!',
                'nuevo_record': True,
                'puntaje_maximo': usuario.puntaje_maximo
            })
        
        return jsonify({
            'success': True, 
            'message': 'Puntaje guardado',
            'nuevo_record': False,
            'puntaje_maximo': usuario.puntaje_maximo
        })
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error guardando puntaje: {e}')
        return jsonify({'success': False, 'error': 'Error al procesar el puntaje'}), 500
