import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_DB_PATH = os.path.join(BASE_DIR, 'auth.db')
CHAT_DB_PATH = os.path.join(BASE_DIR, 'chat.db')


def _connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def init_auth_db():
    """
    Crea la base de datos auth.db con tablas para usuarios y sesiones.
    Tablas:
      - users(id, username, email, password_hash, created_at)
      - sessions(id, user_id -> users.id, token, created_at, expires_at)
    """
    conn = _connect(AUTH_DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            '''
        )
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);')

        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            '''
        )
        cur.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);')

        conn.commit()
    finally:
        conn.close()


def init_chat_db():
    """
    Crea la base de datos chat.db con tablas para conversaciones y mensajes.
    Tablas:
      - conversations(id, user_id, topic, created_at)
      - messages(id, conversation_id -> conversations.id, sender, content, created_at, metadata)
    """
    conn = _connect(CHAT_DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT,
                created_at TEXT NOT NULL
            );
            '''
        )
        cur.execute('CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);')

        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                sender TEXT NOT NULL CHECK(sender IN ("user", "agent")),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            '''
        )
        cur.execute('CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);')

        conn.commit()
    finally:
        conn.close()


def init_all():
    """Inicializa ambas bases de datos."""
    init_auth_db()
    init_chat_db()


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


if __name__ == '__main__':
    init_all()
    print(f"Bases de datos inicializadas en: \n  - {AUTH_DB_PATH}\n  - {CHAT_DB_PATH}")
