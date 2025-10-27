import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from db_init import init_all, AUTH_DB_PATH, CHAT_DB_PATH


# -----------------------------
# App y utilidades generales
# -----------------------------
app = Flask(__name__)
# Habilitar CORS para todas las rutas /api/* (ajusta origins si querés restringir)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "allow_headers": ["Authorization", "Content-Type"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})


def _connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _token_expiry(days: int = 7) -> str:
    return (datetime.utcnow() + timedelta(days=days)).isoformat()


def _json_success(data=None, message=None, status=200):
    resp = {"success": True}
    if message:
        resp["message"] = message
    if data is not None:
        resp["data"] = data
    return jsonify(resp), status


def _json_error(message, status=400, errors=None):
    resp = {"success": False, "message": message}
    if errors:
        resp["errors"] = errors
    return jsonify(resp), status


# -----------------------------
# Inicialización de bases
# -----------------------------
init_all()
print("Bases de datos listas:")
print(f"  - {AUTH_DB_PATH}")
print(f"  - {CHAT_DB_PATH}")


# -----------------------------
# Capa de datos: AUTH
# -----------------------------
def get_user_by_email(email: str):
    with _connect(AUTH_DB_PATH) as conn:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cur.fetchone()


def get_user_by_id(user_id: int):
    with _connect(AUTH_DB_PATH) as conn:
        cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()


def create_user(username: str, email: str, password: str):
    password_hash = generate_password_hash(password)
    now = _now_iso()
    try:
        with _connect(AUTH_DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, password_hash, now),
            )
            user_id = cur.lastrowid
            # Devolver payload básico sin depender de una lectura posterior
            return {"id": user_id, "username": username, "email": email}
    except sqlite3.IntegrityError as e:
        # Violación UNIQUE de username/email
        raise ValueError("Usuario o email ya registrado") from e


def create_session(user_id: int):
    token = str(uuid.uuid4())
    now = _now_iso()
    expires_at = _token_expiry(7)
    with _connect(AUTH_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO sessions (user_id, token, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, token, now, expires_at),
        )
    return token, expires_at


def get_session_by_token(token: str):
    with _connect(AUTH_DB_PATH) as conn:
        cur = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,))
        return cur.fetchone()


def verify_bearer_token(auth_header: str):
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    sess = get_session_by_token(token)
    if not sess:
        return None
    # Validar expiración
    if sess["expires_at"]:
        try:
            if datetime.fromisoformat(sess["expires_at"]) < datetime.utcnow():
                return None
        except Exception:
            return None
    return sess


# -----------------------------
# Endpoints AUTH
# -----------------------------
@app.post('/api/auth/register')
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    errors = []
    if not username:
        errors.append({"field": "username", "message": "El nombre de usuario es requerido"})
    if not email:
        errors.append({"field": "email", "message": "El email es requerido"})
    if not password:
        errors.append({"field": "password", "message": "La contraseña es requerida"})
    if errors:
        return _json_error("Validación fallida", status=400, errors=errors)

    try:
        user = create_user(username, email, password)
    except ValueError as ve:
        return _json_error(str(ve), status=400)

    token, expires_at = create_session(user["id"])
    user_payload = {"id": user["id"], "username": user["username"], "email": user["email"]}
    return _json_success({"token": token, "expires_at": expires_at, "user": user_payload})


@app.post('/api/auth/login')
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return _json_error("Email y contraseña son requeridos", status=400)

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return _json_error("Credenciales inválidas", status=401)

    token, expires_at = create_session(user["id"])
    user_payload = {"id": user["id"], "username": user["username"], "email": user["email"]}
    return _json_success({"token": token, "expires_at": expires_at, "user": user_payload})


@app.get('/api/auth/verify')
def api_verify():
    sess = verify_bearer_token(request.headers.get('Authorization'))
    if not sess:
        return _json_error("Token inválido o expirado", status=401)
    return _json_success({"valid": True})


# -----------------------------
# Capa de datos: CHAT
# -----------------------------
def get_or_create_default_conversation(user_id: int):
    with _connect(CHAT_DB_PATH) as conn:
        cur = conn.execute(
            "SELECT * FROM conversations WHERE user_id = ? ORDER BY id ASC LIMIT 1",
            (user_id,),
        )
        conv = cur.fetchone()
        if conv:
            return conv
        now = _now_iso()
        cur = conn.execute(
            "INSERT INTO conversations (user_id, topic, created_at) VALUES (?, ?, ?)",
            (user_id, "Soporte Técnico IA", now),
        )
        conv_id = cur.lastrowid
        cur = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        return cur.fetchone()


def add_message(conversation_id: int, sender: str, content: str, metadata: str | None = None):
    with _connect(CHAT_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, sender, content, created_at, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, sender, content, _now_iso(), metadata),
        )


def get_last_message_pairs(conversation_id: int, limit_pairs: int = 20):
    # Recupera mensajes y los agrupa en pares user->agent
    with _connect(CHAT_DB_PATH) as conn:
        cur = conn.execute(
            "SELECT sender, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,),
        )
        rows = cur.fetchall()

    pairs = []
    pending_user = None
    for r in rows:
        if r["sender"] == "user":
            pending_user = r["content"]
        elif r["sender"] == "agent" and pending_user is not None:
            pairs.append({"message": pending_user, "response": r["content"]})
            pending_user = None
    return pairs[-limit_pairs:]


def symbolic_ai_reply(user_text: str) -> str:
    txt = user_text.strip().lower()
    # Regla simples a modo de IA simbólica
    rules = [
        ("como funciona", "La app te premia por caminar/correr durante periodos de tiempo, dandote criptomonedas, estas se acumulan hasta llegar a montos cambiables por recompensas, descuentos y mas"),
        ("cómo funciona", "La app te premia por caminar/correr durante periodos de tiempo, dandote criptomonedas, estas se acumulan hasta llegar a montos cambiables por recompensas, descuentos y mas"),
        ("hola", "¡Hola! ¿En qué puedo ayudarte hoy?"),
        ("error", "Entiendo que ves un error. ¿Podrías compartir el mensaje exacto?"),
        ("contraseña", "Para contraseñas, recuerda usar mayúsculas, minúsculas y números."),
        ("registro", "Para registrarte, ve a la sección Registro e ingresa tus datos."),
        ("login", "Si no puedes iniciar sesión, intenta restablecer tu contraseña o verifica tu email."),
        ("pasos", "Los pasos se sincronizan automáticamente. ¿Estás conectado a tu cuenta Samsung?"),
    ]
    for key, resp in rules:
        if key in txt:
            return resp
    return "Gracias por tu mensaje. Estoy analizando tu consulta y te brindaré opciones para resolverla."


# -----------------------------
# Endpoints CHAT
# -----------------------------
@app.get('/api/chat/suggestions')
def api_chat_suggestions():
    sess = verify_bearer_token(request.headers.get('Authorization'))
    if not sess:
        return _json_error("No autorizado", status=401)
    suggestions = [
        "¿Cómo registro una cuenta?",
        "No puedo iniciar sesión",
        "¿Cómo vinculo mi cuenta Samsung?",
        "Mis pasos no se actualizan",
        "¿Cómo recupero mi contraseña?",
    ]
    return _json_success({"suggestions": suggestions})


@app.get('/api/chat/history')
def api_chat_history():
    sess = verify_bearer_token(request.headers.get('Authorization'))
    if not sess:
        return _json_error("No autorizado", status=401)
    user_id = sess["user_id"]
    conv = get_or_create_default_conversation(user_id)
    pairs = get_last_message_pairs(conv["id"], limit_pairs=50)
    return _json_success({"messages": pairs})


@app.post('/api/chat/message')
def api_chat_message():
    sess = verify_bearer_token(request.headers.get('Authorization'))
    if not sess:
        return _json_error("No autorizado", status=401)
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    if not message:
        return _json_error("El mensaje no puede estar vacío", status=400)

    user_id = sess["user_id"]
    conv = get_or_create_default_conversation(user_id)
    # Guardar mensaje de usuario
    add_message(conv["id"], "user", message)
    # Generar respuesta simbólica y guardar
    response = symbolic_ai_reply(message)
    add_message(conv["id"], "agent", response)
    return _json_success({"response": response})


# -----------------------------
# Run
# -----------------------------
if __name__ == '__main__':
    # Modo desarrollo por defecto
    app.run(host='127.0.0.1', port=5000, debug=True)

