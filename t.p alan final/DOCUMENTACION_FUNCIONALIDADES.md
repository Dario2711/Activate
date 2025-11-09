# Documentación Completa de Funcionalidades - Activate

## 📋 Índice
1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Funcionalidades por Módulo](#funcionalidades-por-módulo)
4. [Descripción de Archivos](#descripción-de-archivos)
5. [Flujos de Usuario](#flujos-de-usuario)
6. [Tecnologías Implementadas](#tecnologías-implementadas)

---

## 🎯 Resumen del Proyecto

**Activate** es una aplicación web con sistema de usuarios, ranking y administración. El proyecto implementa:

- ✅ **Sockets TCP/IP** para comunicación distribuida
- ✅ **Serialización** (JSON y Pickle) para intercambio de datos
- ✅ **Arquitectura en Capas** (Presentación, Datos, Infraestructura, Configuración)
- ✅ **Programación Distribuida** con servicios independientes

---

## 🏗️ Arquitectura del Sistema

### Estructura en Capas

```
┌─────────────────────────────────────┐
│   CAPA DE PRESENTACIÓN              │
│   - Templates HTML (Jinja2)        │
│   - Rutas Web (Flask Blueprints)   │
│   - API REST (JSON)                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   CAPA DE DATOS                      │
│   - Modelos (SQLAlchemy)             │
│   - Base de Datos (SQLite)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   CAPA DE INFRAESTRUCTURA           │
│   - TCP Server/Client                │
│   - Servicio Distribuido             │
│   - Serialización                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   CAPA DE CONFIGURACIÓN             │
│   - Settings                         │
└─────────────────────────────────────┘
```

### Servicios del Sistema

1. **Flask Server** (Puerto 5000) - Aplicación web principal
2. **TCP Persistence Server** (Puerto 6000) - Persistencia de datos
3. **Distributed Service** (Puerto 7000) - Notificaciones y estadísticas

---

## 📦 Funcionalidades por Módulo

### 1. Módulo de Presentación (`app/presentation/`)

#### 1.1 Rutas Web (`routes.py`)

**Funcionalidades:**
- **Página Principal (`/`)**: Landing page con QR code y preview del juego
- **Login (`/login`)**: Autenticación de usuarios
- **Registro (`/registro`)**: Creación de nuevas cuentas (con código admin opcional: `6767`)
- **Juego (`/juego`)**: Juego de escritura rápida
- **Perfil (`/perfil`)**: Visualización del perfil del usuario
- **Editar Perfil (`/editar_perfil`)**: Modificación de datos personales y foto
- **Ranking (`/ranking`)**: Top 10 usuarios con mejores puntajes
- **Admin Dashboard (`/admin/dashboard`)**: Panel de administración
- **Logout (`/logout`)**: Cerrar sesión
- **Cómo Funciona (`/como-funciona`)**: Página informativa

**Características:**
- Sistema de sesiones con Flask
- Protección de rutas con decoradores (`@login_required`, `@admin_required`)
- Manejo de archivos (subida de fotos de perfil)
- Validación de formularios

#### 1.2 API REST (`api/routes.py`)

**Endpoints:**

1. **`POST /api/guardar_puntaje`**
   - Guarda el puntaje del usuario
   - Notifica al servicio distribuido si hay nuevo récord
   - Retorna: `{success, message, nuevo_record, puntaje_maximo}`

2. **`POST /api/guardar_puntaje_tcp`**
   - Alternativa que usa el servidor TCP para guardar puntajes
   - Útil para demostrar comunicación distribuida

3. **`GET /api/stats/usuario`**
   - Obtiene estadísticas del usuario actual desde el servicio distribuido
   - Retorna: `{success, stats: {user_id, nombre, email, puntaje_maximo, ...}}`

4. **`GET /api/stats/global`**
   - Obtiene estadísticas globales del sistema
   - Retorna: `{success, stats: {total_usuarios, usuarios_activos, puntaje_promedio, ...}}`

5. **`GET /api/notificaciones`**
   - Obtiene notificaciones del usuario
   - Retorna: `{success, notifications: [...]}`

6. **`POST /api/admin/reiniciar_puntuacion/<usuario_id>`**
   - Reinicia la puntuación de un usuario (solo admin)

7. **`POST /api/admin/eliminar_usuario/<usuario_id>`**
   - Elimina un usuario del sistema (solo admin, requiere contraseña)

#### 1.3 Templates HTML

**Archivos:**
- `base.html`: Template base con navegación y footer
- `index.html`: Página principal con QR code y preview
- `login.html`: Formulario de inicio de sesión
- `registro.html`: Formulario de registro
- `juego.html`: Interfaz del juego de escritura rápida
- `perfil.html`: Visualización del perfil
- `editar_perfil.html`: Edición del perfil
- `ranking.html`: Tabla de mejores puntajes
- `admin/dashboard.html`: Panel de administración
- `como_funciona.html`: Página informativa
- `descargar.html`: Página de descarga de la app

---

### 2. Módulo de Datos (`app/data/`)

#### 2.1 Modelos (`models/db_models.py`)

**Clase Usuario:**
```python
- id: Integer (PK)
- nombre: String(100)
- email: String(100, unique)
- password: String(200) - Hash con Werkzeug
- es_admin: Boolean
- puntaje_maximo: Integer (default: 0)
- fecha_ultimo_juego: DateTime
- foto_perfil: String(200) (default: 'default.svg')
- biografia: Text
- fecha_registro: DateTime (default: now)
```

**Métodos:**
- `set_password(password)`: Hashea y guarda contraseña
- `check_password(password)`: Verifica contraseña

#### 2.2 Base de Datos (`database.py`)

**Funcionalidades:**
- Inicialización de SQLAlchemy
- Creación automática de tablas
- Configuración de conexión SQLite

**Ubicación:** `instance/usuarios.db` o `usuarios.db` (raíz)

---

### 3. Módulo de Infraestructura (`app/infrastructure/`)

#### 3.1 TCP Server (`tcp_server.py`)

**Propósito:** Servidor TCP independiente para persistencia de datos

**Puerto:** 6000 (configurable con `TCP_PERSIST_PORT`)

**Protocolo:**
- Cliente envía JSON por línea: `{"action": "...", ...}\n`
- Servidor responde JSON por línea: `{"success": true/false, ...}\n`

**Acciones soportadas:**
- `save_score`: Guarda puntaje de usuario
  ```json
  {"action": "save_score", "user_id": 1, "puntaje": 100}
  ```
- `ping`: Verifica conectividad
  ```json
  {"action": "ping"}
  ```

**Características:**
- Threading para múltiples clientes
- Manejo de errores robusto
- Acceso directo a SQLite (sin Flask context)

#### 3.2 TCP Client (`tcp_client.py`)

**Funcionalidades:**
- Cliente para comunicarse con el TCP Server
- Función `save_score_via_tcp(user_id, puntaje)`
- Timeout configurable (default: 3 segundos)
- Manejo de errores de conexión

#### 3.3 Servicio Distribuido (`distributed_service.py`)

**Propósito:** Servicio independiente para notificaciones y estadísticas

**Puerto:** 7000 (configurable con `DISTRIBUTED_PORT`)

**Clase DistributedService:**
- `get_user_stats(user_id)`: Estadísticas de un usuario
- `get_global_stats()`: Estadísticas globales del sistema
- `add_notification(user_id, message, type)`: Agrega notificación
- `get_notifications(user_id)`: Obtiene notificaciones

**Clase DistributedServiceClient:**
- Cliente para comunicarse con el servicio distribuido
- Métodos: `get_user_stats()`, `get_global_stats()`, `add_notification()`, `get_notifications()`

**Acciones soportadas:**
- `get_user_stats`: `{"action": "get_user_stats", "user_id": 1}`
- `get_global_stats`: `{"action": "get_global_stats"}`
- `add_notification`: `{"action": "add_notification", "user_id": 1, "message": "...", "type": "info"}`
- `get_notifications`: `{"action": "get_notifications", "user_id": 1}`
- `ping`: `{"action": "ping"}`

#### 3.4 Serialización (`serialization.py`)

**Clase Serializer:**
- `serialize_json(data)`: Serializa a JSON string
- `deserialize_json(data)`: Deserializa desde JSON string
- `serialize_pickle(data)`: Serializa a bytes con Pickle
- `deserialize_pickle(data)`: Deserializa desde bytes con Pickle
- `serialize_pickle_base64(data)`: Serializa a string base64
- `deserialize_pickle_base64(data)`: Deserializa desde base64
- `serialize_hybrid(data)`: Intenta JSON, usa Pickle si falla
- `deserialize_hybrid(data)`: Deserializa formato híbrido

**Funciones de utilidad:**
- `serialize(data, method='json')`: Serializa con método especificado
- `deserialize(data, method='json')`: Deserializa con método especificado

---

### 4. Módulo de Configuración (`app/core/config/`)

#### 4.1 Settings (`settings.py`)

**Configuraciones:**
- `SECRET_KEY`: Clave secreta para sesiones Flask
- `SQLALCHEMY_DATABASE_URI`: URI de conexión a base de datos
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Desactivado para performance
- `UPLOAD_FOLDER`: Carpeta para subida de archivos
- `MAX_CONTENT_LENGTH`: Tamaño máximo de archivos (16MB)

**Método `init_app(app)`:**
- Crea carpetas necesarias (uploads)
- Inicializa configuraciones

---

### 5. Módulo Principal (`app/`)

#### 5.1 App Factory (`app.py`)

**Funcionalidades:**
- Crea la aplicación Flask
- Configura templates y static folders
- Inicializa base de datos
- Registra blueprints (main, api)
- Define decoradores: `login_required`, `admin_required`
- Context processor para inyectar usuario en templates

#### 5.2 Entry Point (`__main__.py`)

**Propósito:** Punto de entrada para ejecutar la app
```python
python -m app
```

---

## 📁 Descripción de Archivos

### Archivos Principales

#### Backend (Python)

| Archivo | Propósito | Funcionalidades Clave |
|---------|-----------|----------------------|
| `app/app.py` | Factory de la aplicación Flask | Crea app, registra blueprints, decoradores |
| `app/__main__.py` | Punto de entrada | Ejecuta el servidor Flask |
| `app/presentation/routes.py` | Rutas web principales | Login, registro, juego, perfil, admin |
| `app/presentation/api/routes.py` | API REST | Endpoints JSON para frontend |
| `app/data/models/db_models.py` | Modelos de datos | Clase Usuario con SQLAlchemy |
| `app/data/database.py` | Configuración DB | Inicialización SQLAlchemy |
| `app/infrastructure/tcp_server.py` | Servidor TCP | Persistencia distribuida |
| `app/infrastructure/tcp_client.py` | Cliente TCP | Comunicación con TCP server |
| `app/infrastructure/distributed_service.py` | Servicio distribuido | Notificaciones y estadísticas |
| `app/infrastructure/serialization.py` | Serialización | JSON, Pickle, híbrido |
| `app/core/config/settings.py` | Configuración | Settings de la aplicación |

#### Frontend (HTML/CSS/JS)

| Archivo | Propósito | Funcionalidades Clave |
|---------|-----------|----------------------|
| `templates/base.html` | Template base | Navegación, footer, estructura común |
| `templates/index.html` | Página principal | Landing con QR code y preview |
| `templates/juego.html` | Juego | Interfaz del juego de escritura rápida |
| `templates/login.html` | Login | Formulario de autenticación |
| `templates/registro.html` | Registro | Formulario de registro |
| `templates/perfil.html` | Perfil | Visualización del perfil |
| `templates/editar_perfil.html` | Editar perfil | Formulario de edición |
| `templates/ranking.html` | Ranking | Top 10 usuarios |
| `templates/admin/dashboard.html` | Admin | Panel de administración |
| `static/css/styles.css` | Estilos | Estilos personalizados |

#### Scripts de Utilidad

| Archivo | Propósito |
|---------|-----------|
| `scripts/init_db.py` | Inicializar base de datos |
| `scripts/reset_db.py` | Resetear base de datos |
| `scripts/fix_db.py` | Reparar base de datos |
| `scripts/check_db.py` | Verificar base de datos |

#### Scripts de Inicio

| Archivo | Propósito |
|---------|-----------|
| `iniciar_servidor.bat` | Inicia servidor Flask |
| `iniciar.bat` | Inicia la aplicacion

#### Documentación

| Archivo | Propósito |
|---------|-----------|
| `ARQUITECTURA_DISTRIBUIDA.md` | Documentación técnica de arquitectura |
| `DOCUMENTACION_FUNCIONALIDADES.md` | Este archivo - Documentación completa |
| `README.md` | Instrucciones de Git |

---

## 🔄 Flujos de Usuario

### 1. Flujo de Registro y Login

```
Usuario → /registro → Completa formulario → Crea cuenta → /login → Inicia sesión → / (home)
```

**Detalles:**
- Validación de email único
- Hash de contraseña con Werkzeug
- Código admin `6767` para crear administradores
- Sesión iniciada con `session['user_id']` y `session['es_admin']`

### 2. Flujo de Juego

```
Usuario logueado → /juego → Click "Comenzar" → Escribe texto → Completa o pierde vidas
→ POST /api/guardar_puntaje → Si nuevo récord: notifica servicio distribuido
→ Muestra resultado → Opción "Jugar de nuevo"
```

**Detalles:**
- 3 vidas por partida
- Puntos por palabra completada
- Guardado automático al terminar
- Notificación al servicio distribuido si hay nuevo récord

### 3. Flujo de Administración

```
Admin → /admin/dashboard → Ver usuarios → Reiniciar puntaje / Eliminar usuario
→ Confirmación → Actualización en DB → Redirección a dashboard
```

**Detalles:**
- Solo usuarios con `es_admin=True`
- Validación de contraseña para eliminar usuarios
- No puede eliminar su propia cuenta

### 4. Flujo de Comunicación Distribuida

```
Flask App → POST /api/guardar_puntaje → Nuevo récord detectado
→ DistributedServiceClient → TCP Socket → Distributed Service (Puerto 7000)
→ add_notification() → Guarda en cola de notificaciones
→ Usuario puede ver: GET /api/notificaciones
```

**Detalles:**
- Comunicación asíncrona
- Tolerante a fallos (si servicio no disponible, app sigue funcionando)
- Serialización JSON para comunicación

---

## 🛠️ Tecnologías Implementadas

### Backend
- **Flask 2.3.3**: Framework web
- **SQLAlchemy 3.1.1**: ORM para base de datos
- **Werkzeug 2.3.7**: Utilidades (hash de contraseñas, manejo de archivos)
- **Python 3.x**: Lenguaje principal

### Frontend
- **Bootstrap 5.3.0**: Framework CSS
- **Bootstrap Icons**: Iconos
- **JavaScript (Vanilla)**: Lógica del juego
- **Jinja2**: Motor de templates

### Base de Datos
- **SQLite**: Base de datos relacional

### Comunicación
- **Sockets TCP/IP**: Comunicación entre servicios
- **JSON**: Serialización de datos
- **Pickle**: Serialización de objetos complejos

### Arquitectura
- **Arquitectura en Capas**: Separación de responsabilidades
- **Programación Distribuida**: Servicios independientes
- **Blueprints**: Organización modular de rutas Flask
- **Factory Pattern**: Creación de aplicación Flask

---

## 🚀 Cómo Ejecutar

### Opción 1: Iniciar Todo (Recomendado)
```bash
iniciar_todo.bat
```

### Opción 2: Servicios Individuales

**Servidor TCP:**
```bash
python -m app.infrastructure.tcp_server
```

**Servicio Distribuido:**
```bash
python -m app.infrastructure.distributed_service
```

**Servidor Flask:**
```bash
python -m app
# O
python -m flask run
```

### Acceso
- **Web App**: http://localhost:5000
- **TCP Server**: localhost:6000
- **Distributed Service**: localhost:7000

---

## 📊 Resumen de Funcionalidades

### Usuario Regular
- ✅ Registro y login
- ✅ Jugar juego de escritura rápida
- ✅ Ver perfil y editar datos
- ✅ Subir foto de perfil
- ✅ Ver ranking de mejores puntajes
- ✅ Recibir notificaciones de nuevos récords

### Administrador
- ✅ Todas las funcionalidades de usuario
- ✅ Panel de administración
- ✅ Ver todos los usuarios
- ✅ Reiniciar puntajes
- ✅ Eliminar usuarios

### Sistema
- ✅ Persistencia de datos (SQLite)
- ✅ Comunicación TCP entre servicios
- ✅ Servicio distribuido de notificaciones
- ✅ Serialización JSON y Pickle
- ✅ Arquitectura en capas
- ✅ API REST para frontend

---

## 📝 Notas Importantes

1. **Código Admin**: `6767` - Usar en registro para crear cuenta de administrador
2. **Base de Datos**: Se crea automáticamente en `instance/usuarios.db`
3. **Fotos de Perfil**: Se guardan en `presentation/web/static/uploads/`
4. **Tolerancia a Fallos**: El sistema funciona aunque los servicios distribuidos no estén disponibles
5. **Puertos**: Configurables mediante variables de entorno

---

## 🔍 Características Técnicas Destacadas

1. **Sockets TCP/IP**: Implementación completa de servidor y cliente
2. **Serialización**: Múltiples métodos (JSON, Pickle, Híbrido)
3. **Arquitectura en Capas**: Separación clara de responsabilidades
4. **Programación Distribuida**: Servicios independientes comunicándose
5. **Threading**: Manejo concurrente de conexiones
6. **Seguridad**: Hash de contraseñas, validación de sesiones
7. **API REST**: Endpoints JSON bien estructurados
8. **Templates**: Sistema de templates reutilizables con Jinja2

---

*Documentación generada para el proyecto Activate - Sistema de Juego de Escritura Rápida con Arquitectura Distribuida*

## NUEVO: Sistema de Recompensas y Logros

### Descripción:
Los usuarios pueden canjear sus puntos obtenidos en el juego por recompensas realistas (descuentos, cupones, sorteos, gift cards, merchandising, etc.).
- Cada recompensa requiere un mínimo de puntos.
- Al canjear una recompensa, esta queda guardada en el perfil del usuario como logro.
- Todas las recompensas y logros pueden ser consultadas en el historial de canjes desde el perfil.

**Rutas principales:**
- `/recompensas`: Catálogo de recompensas y formulario de canje.
- `/perfil`: Visualización de logros/canjes obtenidos.

### Ejemplos de recompensas:
- 10% OFF en Tienda Samsung
- Auriculares Galaxy Buds (descuento o sorteo)
- Gift Card PedidosYa
- Stickers y Merchandising
- Entrenamiento personalizado

### Flujo resumido de canje:
```
Usuario → /recompensas → Ve catálogo → Si tiene puntos suficientes, canjea → Se muestra mensaje de éxito y se descuenta el puntaje → El canje aparece en su historial/logros (/perfil)
```

### Tabla de nuevos modelos en DB:
- `Recompensa`: catálogo de recompensas.
- `CanjeRecompensa`: historial (logros/canjes) por usuario.

## CAMBIOS EN LA DOCUMENTACIÓN DE FUNCIONALIDADES

- Agregado apartado en Índice, Flujos de Usuario, Funcionalidades por Módulo (Presentación/Data), y Descripción de Archivos para este sistema de recompensas/logros.
- Actualizados los archivos/templates impactados: `routes.py`, `perfil.html`, `recompensas.html`, `base.html`, `db_models.py`.
*Qué se guarda (modelo de datos)*
El esquema incorpora dos tablas nuevas, además de Usuario:
#Usuario
Contiene, entre otros, puntaje_maximo (entero). En tu implementación actual se usa como “saldo” para habilitar o bloquear el canje desde la vista. 

#Recompensa
id, nombre, descripcion, puntos (costo del canje), imagen. Es el catálogo. 

#CanjeRecompensa
usuario_id, recompensa_id, fecha y relación a Recompensa. Es el historial de canjes que luego se muestra como “logros”. 

La documentación funcional también lo presenta así: catálogo (Recompensa) + historial (CanjeRecompensa); y define el flujo “ver catálogo → canjear → descontar puntos → mostrar en /perfil”. 

*Flujo técnico del canje (lo que hace el backend cuando apretás “Canjear”)*
GET /recompensas: carga recompensas (catálogo), usuario y (si existen) logros del usuario para listar el historial. 

*POST /recompensas (form):*
Llega recompensa_id. 

Validaciones esperables (implícitas por el HTML y por la doc):

Que la recompensa exista. 

Que el usuario tenga puntos suficientes (la vista ya deshabilita el botón; el backend debería volver a validar). 

*Persistencia:*
Se crea un CanjeRecompensa(usuario_id, recompensa_id, fecha=now). 
Descuento de puntos: la doc dice que “se descuenta el puntaje” al canjear; en el modelo actual no existe un campo “saldo” separado, por lo que la app está usando puntaje_maximo para decidir si podés canjear. El descuento real debería actualizar el campo que usen como “saldo”. (Ver recomendaciones más abajo).

#Respuesta: muestra mensaje de éxito y el canje aparece en el historial (se refleja en la sección “Tus logros y canjes”).

*Reglas de negocio clave*
Costo en puntos por recompensa: Recompensa.puntos. 
Habilitación del botón: depende de usuario.puntaje_maximo >= recompensa.puntos (lógica en el template). 

Registro de logro: cada canje crea un CanjeRecompensa y se muestra con nombre, imagen, descripción, puntos gastados y fecha.

*Cómo agregar/editar* 
Para ampliar el catálogo, insertás filas en Recompensa con nombre, descripcion, puntos e imagen (ruta en static/img/). La vista ya las renderiza automáticamente en la grilla.

*Validar también en backend*
Aunque el botón se deshabilite en el HTML, el POST debe verificar saldo ≥ costo, por seguridad. (Defensa en profundidad). 

*Transacción atómica*
En el handler del POST: (a) leer recompensa y usuario, (b) chequear saldo, (c) restar saldo y (d) crear CanjeRecompensa, todo dentro de una misma transacción para evitar estados inconsistentes si hay concurrencia. 

*Mensajes y estados vacíos*
Mostrar toast/alert de éxito o error después del POST.
En “Tus logros y canjes”, si no hay datos, mostrar un texto guía (“Aún no tenés canjes”). La plantilla ya contempla la sección solo si logros existe; podés agregar un estado vacío si viene lista vacía. 



