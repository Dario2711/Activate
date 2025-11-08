import socket
import threading
import json
import sqlite3
import os
from datetime import datetime

# TCP persistence server: handles simple JSON commands over TCP to read/write data
# Protocol:
#  - Client sends a single line with a JSON object, e.g.:
#    {"action":"save_score","user_id":1,"puntaje":123}
#  - Server replies with a single line JSON: {"success": true, ...}
#
# This intentionally uses sqlite3 directly to avoid depending on a Flask app context.

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'usuarios.db')
HOST = os.environ.get('TCP_PERSIST_HOST', '127.0.0.1')
PORT = int(os.environ.get('TCP_PERSIST_PORT', '6000'))

# Ensure DB exists with expected schema minimally (id, puntaje_maximo, fecha_ultimo_juego)
SCHEMA_CHECK = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    email TEXT UNIQUE,
    password TEXT,
    es_admin BOOLEAN DEFAULT 0,
    puntaje_maximo INTEGER DEFAULT 0,
    fecha_ultimo_juego TEXT,
    foto_perfil TEXT,
    biografia TEXT,
    fecha_registro TEXT
);
"""

def handle_client(conn, addr):
    try:
        data = b''
        # Read until newline or connection close
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in chunk:
                break
        if not data:
            return
        # support either newline-terminated or raw single JSON message
        try:
            payload = json.loads(data.decode('utf-8').strip())
        except json.JSONDecodeError:
            conn.sendall((json.dumps({"success": False, "error": "invalid_json"}) + "\n").encode('utf-8'))
            return

        action = payload.get('action')
        if action == 'save_score':
            user_id = payload.get('user_id')
            puntaje = payload.get('puntaje')
            if not isinstance(user_id, int) or not isinstance(puntaje, int):
                conn.sendall((json.dumps({"success": False, "error": "invalid_params"}) + "\n").encode('utf-8'))
                return
            try:
                with sqlite3.connect(DB_PATH) as con:
                    cur = con.cursor()
                    # Ensure table exists
                    cur.executescript(SCHEMA_CHECK)
                    # Read current score
                    cur.execute("SELECT puntaje_maximo FROM usuarios WHERE id=?", (user_id,))
                    row = cur.fetchone()
                    if not row:
                        conn.sendall((json.dumps({"success": False, "error": "user_not_found"}) + "\n").encode('utf-8'))
                        return
                    current_max = row[0] or 0
                    nuevo_record = puntaje > current_max
                    if nuevo_record:
                        cur.execute(
                            "UPDATE usuarios SET puntaje_maximo=?, fecha_ultimo_juego=? WHERE id=?",
                            (puntaje, datetime.utcnow().isoformat(), user_id)
                        )
                        con.commit()
                    conn.sendall((json.dumps({
                        "success": True,
                        "nuevo_record": nuevo_record,
                        "puntaje_maximo": max(puntaje, current_max)
                    }) + "\n").encode('utf-8'))
            except Exception as e:
                conn.sendall((json.dumps({"success": False, "error": "db_error", "details": str(e)}) + "\n").encode('utf-8'))
        elif action == 'ping':
            conn.sendall((json.dumps({"success": True, "pong": True}) + "\n").encode('utf-8'))
        else:
            conn.sendall((json.dumps({"success": False, "error": "unknown_action"}) + "\n").encode('utf-8'))
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()


def start_server(host: str = HOST, port: int = PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        print(f"[TCP] Persistence server listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == '__main__':
    start_server()
