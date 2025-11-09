"""
Servicio Distribuido de Notificaciones y Estadísticas
Este servicio se comunica con el servidor principal usando sockets y serialización
"""
import socket
import threading
import json
import pickle
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuración del servicio distribuido
DISTRIBUTED_HOST = os.environ.get('DISTRIBUTED_HOST', '127.0.0.1')
DISTRIBUTED_PORT = int(os.environ.get('DISTRIBUTED_PORT', '7000'))
MAIN_SERVER_HOST = os.environ.get('MAIN_SERVER_HOST', '127.0.0.1')
MAIN_SERVER_PORT = int(os.environ.get('MAIN_SERVER_PORT', '5000'))

# Ruta a la base de datos - usar la misma lógica que tcp_server.py
# Intentar múltiples ubicaciones para compatibilidad
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATHS = [
    os.path.join(BASE_DIR, 'instance', 'usuarios.db'),  # Preferido: instance/usuarios.db
    os.path.join(BASE_DIR, 'usuarios.db'),  # Alternativa: raíz del proyecto
    os.path.join(os.path.dirname(BASE_DIR), 'instance', 'usuarios.db'),  # Alternativa: nivel superior
]

# Encontrar la base de datos existente
DB_PATH = None
for path in DB_PATHS:
    if os.path.exists(path):
        DB_PATH = path
        break

# Si no existe, usar la primera opción por defecto (se creará si es necesario)
if DB_PATH is None:
    DB_PATH = DB_PATHS[0]
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class DistributedService:
    """Servicio distribuido que maneja notificaciones y estadísticas"""
    
    def __init__(self):
        self.stats_cache = {}
        self.notifications_queue = []
        self.running = False
        
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de un usuario desde la base de datos"""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, nombre, email, puntaje_maximo, 
                           fecha_ultimo_juego, fecha_registro
                    FROM usuarios WHERE id = ?
                """, (user_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row['id'],
                        'nombre': row['nombre'],
                        'email': row['email'],
                        'puntaje_maximo': row['puntaje_maximo'],
                        'fecha_ultimo_juego': row['fecha_ultimo_juego'],
                        'fecha_registro': row['fecha_registro']
                    }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
        return {}
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales del sistema"""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # Total de usuarios
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                total_usuarios = cursor.fetchone()[0]
                
                # Usuarios activos (con puntaje > 0)
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE puntaje_maximo > 0")
                usuarios_activos = cursor.fetchone()[0]
                
                # Puntaje promedio
                cursor.execute("SELECT AVG(puntaje_maximo) FROM usuarios WHERE es_admin = 0")
                promedio = cursor.fetchone()[0] or 0
                
                # Puntaje máximo global
                cursor.execute("SELECT MAX(puntaje_maximo) FROM usuarios WHERE es_admin = 0")
                max_puntaje = cursor.fetchone()[0] or 0
                
                return {
                    'total_usuarios': total_usuarios,
                    'usuarios_activos': usuarios_activos,
                    'puntaje_promedio': round(promedio, 2),
                    'puntaje_maximo_global': max_puntaje,
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error obteniendo estadísticas globales: {e}")
        return {}
    
    def add_notification(self, user_id: int, message: str, notification_type: str = 'info'):
        """Agrega una notificación a la cola"""
        notification = {
            'user_id': user_id,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.notifications_queue.append(notification)
        # Mantener solo las últimas 100 notificaciones
        if len(self.notifications_queue) > 100:
            self.notifications_queue.pop(0)
    
    def get_notifications(self, user_id: Optional[int] = None) -> list:
        """Obtiene notificaciones, opcionalmente filtradas por usuario"""
        if user_id:
            return [n for n in self.notifications_queue if n['user_id'] == user_id]
        return self.notifications_queue[-10:]  # Últimas 10 notificaciones
    
    def handle_client_request(self, conn: socket.socket, addr: tuple):
        """Maneja las peticiones de clientes al servicio distribuido"""
        try:
            # Leer datos del cliente
            data = b''
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n' in chunk:
                    break
            
            if not data:
                return
            
            # Deserializar usando JSON
            try:
                request = json.loads(data.decode('utf-8').strip())
            except json.JSONDecodeError:
                # Intentar con pickle si JSON falla
                try:
                    request = pickle.loads(data)
                except Exception:
                    conn.sendall((json.dumps({
                        "success": False, 
                        "error": "invalid_request_format"
                    }) + "\n").encode('utf-8'))
                    return
            
            action = request.get('action')
            response = {"success": False, "error": "unknown_action"}
            
            if action == 'get_user_stats':
                user_id = request.get('user_id')
                if user_id:
                    stats = self.get_user_stats(user_id)
                    response = {"success": True, "stats": stats}
            
            elif action == 'get_global_stats':
                stats = self.get_global_stats()
                response = {"success": True, "stats": stats}
            
            elif action == 'add_notification':
                user_id = request.get('user_id')
                message = request.get('message')
                notif_type = request.get('type', 'info')
                if user_id and message:
                    self.add_notification(user_id, message, notif_type)
                    response = {"success": True, "message": "Notification added"}
            
            elif action == 'get_notifications':
                user_id = request.get('user_id')
                notifications = self.get_notifications(user_id)
                response = {"success": True, "notifications": notifications}
            
            elif action == 'ping':
                response = {"success": True, "pong": True, "service": "distributed"}
            
            # Enviar respuesta serializada en JSON
            conn.sendall((json.dumps(response) + "\n").encode('utf-8'))
            
        except Exception as e:
            error_response = json.dumps({
                "success": False,
                "error": "server_error",
                "details": str(e)
            })
            conn.sendall((error_response + "\n").encode('utf-8'))
        finally:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            conn.close()
    
    def start_server(self, host: str = DISTRIBUTED_HOST, port: int = DISTRIBUTED_PORT):
        """Inicia el servidor del servicio distribuido"""
        self.running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(5)
            print(f"[DISTRIBUTED] Servicio distribuido iniciado en {host}:{port}")
            print(f"[DISTRIBUTED] Listo para recibir conexiones...")
            
            while self.running:
                try:
                    conn, addr = s.accept()
                    print(f"[DISTRIBUTED] Conexión recibida de {addr}")
                    thread = threading.Thread(
                        target=self.handle_client_request, 
                        args=(conn, addr), 
                        daemon=True
                    )
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"[DISTRIBUTED] Error aceptando conexión: {e}")
    
    def stop_server(self):
        """Detiene el servidor"""
        self.running = False


# Cliente para comunicarse con el servicio distribuido
class DistributedServiceClient:
    """Cliente para comunicarse con el servicio distribuido"""
    
    def __init__(self, host: str = DISTRIBUTED_HOST, port: int = DISTRIBUTED_PORT):
        self.host = host
        self.port = port
    
    def _send_request(self, payload: Dict[str, Any], timeout: float = 3.0) -> tuple:
        """Envía una petición al servicio distribuido"""
        try:
            data = (json.dumps(payload) + "\n").encode('utf-8')
            with socket.create_connection((self.host, self.port), timeout=timeout) as s:
                s.sendall(data)
                # Leer respuesta
                buf = b''
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                    if b"\n" in chunk:
                        break
                try:
                    resp = json.loads(buf.decode('utf-8').strip())
                    ok = bool(resp.get('success'))
                    return ok, resp
                except json.JSONDecodeError:
                    return False, {"error": "invalid_response"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_user_stats(self, user_id: int) -> tuple:
        """Obtiene estadísticas de un usuario"""
        return self._send_request({
            'action': 'get_user_stats',
            'user_id': user_id
        })
    
    def get_global_stats(self) -> tuple:
        """Obtiene estadísticas globales"""
        return self._send_request({
            'action': 'get_global_stats'
        })
    
    def add_notification(self, user_id: int, message: str, notif_type: str = 'info') -> tuple:
        """Agrega una notificación"""
        return self._send_request({
            'action': 'add_notification',
            'user_id': user_id,
            'message': message,
            'type': notif_type
        })
    
    def get_notifications(self, user_id: Optional[int] = None) -> tuple:
        """Obtiene notificaciones"""
        payload = {'action': 'get_notifications'}
        if user_id:
            payload['user_id'] = user_id
        return self._send_request(payload)


if __name__ == '__main__':
    service = DistributedService()
    try:
        service.start_server()
    except KeyboardInterrupt:
        print("\n[DISTRIBUTED] Deteniendo servicio...")
        service.stop_server()

