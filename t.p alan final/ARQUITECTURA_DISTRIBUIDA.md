# Arquitectura Distribuida - Documentación

## Resumen de Implementación

Este proyecto ahora cuenta con una arquitectura distribuida completa que incluye:

### ✅ Componentes Implementados

1. **Sockets TCP/IP**
   - Servidor TCP de persistencia (`tcp_server.py`) - Puerto 6000
   - Cliente TCP (`tcp_client.py`)
   - Servicio distribuido (`distributed_service.py`) - Puerto 7000
   - Cliente del servicio distribuido (`DistributedServiceClient`)

2. **Serialización**
   - JSON para datos simples (ya implementado)
   - Pickle para objetos complejos (nuevo - `serialization.py`)
   - Serialización híbrida (JSON + Pickle según necesidad)

3. **Arquitectura en Capas**
   - **Capa de Presentación**: `app/presentation/` (rutas web y API)
   - **Capa de Datos**: `app/data/` (modelos y base de datos)
   - **Capa de Infraestructura**: `app/infrastructure/` (sockets, TCP, servicios distribuidos)
   - **Capa de Configuración**: `app/core/config/` (configuraciones)

4. **Programación Distribuida**
   - Servicio distribuido de notificaciones y estadísticas
   - Comunicación entre servicios mediante sockets
   - Separación de responsabilidades entre servicios

## Servicios del Sistema

### 1. Servidor Flask Principal (Puerto 5000)
- Aplicación web principal
- API REST para el frontend
- Gestión de usuarios y sesiones

### 2. Servidor TCP de Persistencia (Puerto 6000)
- Persistencia de puntajes mediante TCP
- Comunicación mediante JSON
- Operaciones: `save_score`, `ping`

### 3. Servicio Distribuido (Puerto 7000)
- Gestión de notificaciones
- Estadísticas de usuarios y globales
- Comunicación mediante JSON y Pickle
- Operaciones:
  - `get_user_stats`: Obtiene estadísticas de un usuario
  - `get_global_stats`: Obtiene estadísticas globales del sistema
  - `add_notification`: Agrega una notificación
  - `get_notifications`: Obtiene notificaciones de un usuario
  - `ping`: Verifica conectividad

## Uso de la Serialización

### JSON (Datos Simples)
```python
from app.infrastructure.serialization import serialize, deserialize

# Serializar
data = {"user_id": 1, "puntaje": 100}
json_str = serialize(data, method='json')

# Deserializar
data = deserialize(json_str, method='json')
```

### Pickle (Objetos Complejos)
```python
# Serializar objetos complejos
class MiObjeto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj = MiObjeto(1, 2)
pickled = serialize(obj, method='pickle_base64')

# Deserializar
obj = deserialize(pickled, method='pickle_base64')
```

### Serialización Híbrida
```python
from app.infrastructure.serialization import Serializer

# Intenta JSON primero, usa Pickle si es necesario
serialized = Serializer.serialize_hybrid(data)
deserialized = Serializer.deserialize_hybrid(serialized)
```

## API Endpoints Nuevos

### Estadísticas
- `GET /api/stats/usuario` - Estadísticas del usuario actual
- `GET /api/stats/global` - Estadísticas globales del sistema

### Notificaciones
- `GET /api/notificaciones` - Notificaciones del usuario actual

### Puntajes (Mejorado)
- `POST /api/guardar_puntaje` - Ahora notifica al servicio distribuido cuando hay nuevo récord

## Iniciar el Sistema

### Opción 1: Iniciar Todo (Recomendado)
```bash
iniciar_todo.bat
```
Inicia todos los servicios:
- TCP Persistence Server (Puerto 6000)
- Distributed Service (Puerto 7000)
- Flask Server (Puerto 5000)

### Opción 2: Iniciar Servicios Individualmente

**Servidor TCP de Persistencia:**
```bash
python -m app.infrastructure.tcp_server
```

**Servicio Distribuido:**
```bash
python -m app.infrastructure.distributed_service
# O usar:
iniciar_servicio_distribuido.bat
```

**Servidor Flask:**
```bash
python -m app
# O usar:
iniciar_servidor.bat
```

## Configuración

Las configuraciones se pueden modificar mediante variables de entorno:

- `TCP_PERSIST_HOST`: Host del servidor TCP (default: 127.0.0.1)
- `TCP_PERSIST_PORT`: Puerto del servidor TCP (default: 6000)
- `DISTRIBUTED_HOST`: Host del servicio distribuido (default: 127.0.0.1)
- `DISTRIBUTED_PORT`: Puerto del servicio distribuido (default: 7000)
- `MAIN_SERVER_HOST`: Host del servidor principal (default: 127.0.0.1)
- `MAIN_SERVER_PORT`: Puerto del servidor principal (default: 5000)

## Ejemplo de Uso del Cliente Distribuido

```python
from app.infrastructure.distributed_service import DistributedServiceClient

# Crear cliente
client = DistributedServiceClient()

# Obtener estadísticas de usuario
ok, stats = client.get_user_stats(user_id=1)
if ok:
    print(f"Puntaje máximo: {stats['stats']['puntaje_maximo']}")

# Obtener estadísticas globales
ok, global_stats = client.get_global_stats()
if ok:
    print(f"Total usuarios: {global_stats['stats']['total_usuarios']}")

# Agregar notificación
ok, resp = client.add_notification(
    user_id=1,
    message="¡Nuevo récord alcanzado!",
    notif_type='success'
)

# Obtener notificaciones
ok, resp = client.get_notifications(user_id=1)
if ok:
    for notification in resp['notifications']:
        print(f"{notification['message']} - {notification['timestamp']}")
```

## Arquitectura de Comunicación

```
┌─────────────────┐
│  Frontend (Web) │
└────────┬─────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Flask Server    │◄──┐
│ (Puerto 5000)   │   │
└────────┬────────┘   │
         │            │
         │ TCP        │ TCP
         ▼            │
┌─────────────────┐   │
│ TCP Persistence │   │
│ (Puerto 6000)   │   │
└─────────────────┘   │
                      │
         ┌────────────┘
         │ TCP/JSON
         ▼
┌─────────────────┐
│ Distributed     │
│ Service         │
│ (Puerto 7000)   │
└─────────────────┘
```

## Notas Importantes

1. **Orden de Inicio**: Se recomienda iniciar primero el TCP Server y el Distributed Service antes del Flask Server.

2. **Tolerancia a Fallos**: El sistema está diseñado para funcionar aunque el servicio distribuido no esté disponible. Las operaciones críticas (guardar puntajes) funcionan sin él.

3. **Base de Datos**: El servicio distribuido busca la base de datos en múltiples ubicaciones:
   - `instance/usuarios.db` (preferido)
   - `usuarios.db` (raíz del proyecto)

4. **Threading**: Todos los servicios usan threading para manejar múltiples conexiones simultáneas.

## Mejoras Futuras Posibles

- Implementar un sistema de mensajería más robusto (RabbitMQ, Redis)
- Agregar autenticación entre servicios
- Implementar balanceo de carga
- Agregar logging distribuido
- Implementar cache distribuido

