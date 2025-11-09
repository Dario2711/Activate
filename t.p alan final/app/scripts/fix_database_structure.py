import os
import sqlite3
from datetime import datetime, timedelta

def fix_database():
    # Ruta a la base de datos
    db_path = 'instance/usuarios.db'
    backup_path = 'instance/usuarios_backup_fix.db'
    
    # Hacer una copia de seguridad adicional
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Se ha creado una copia de seguridad en {backup_path}")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar la estructura actual de la tabla
        cursor.execute("PRAGMA table_info(configuracion_sistema)")
        columns = cursor.fetchall()
        print("\nEstructura actual de la tabla configuracion_sistema:")
        for col in columns:
            print(f"Columna {col[1]} - Tipo: {col[2]}")
        
        # Crear una tabla temporal con la estructura correcta
        print("\nCreando nueva estructura...")
        
        # 1. Crear una tabla temporal con la estructura correcta
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_sistema_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ultimo_reinicio TIMESTAMP NOT NULL,
            proximo_reinicio TIMESTAMP NOT NULL
        )
        """)
        
        # 2. Copiar los datos existentes a la nueva tabla
        print("Copiando datos existentes...")
        cursor.execute("""
        INSERT INTO configuracion_sistema_new (id, ultimo_reinicio, proximo_reinicio)
        SELECT 
            id,
            CASE 
                WHEN typeof(ultimo_reinicio) = 'text' THEN datetime(ultimo_reinicio)
                ELSE datetime(ultimo_reinicio, 'unixepoch')
            END,
            CASE 
                WHEN typeof(proximo_reinicio) = 'text' THEN datetime(proximo_reinicio)
                ELSE datetime(proximo_reinicio, 'unixepoch')
            END
        FROM configuracion_sistema
        """)
        
        # 3. Eliminar la tabla antigua
        print("Reemplazando la tabla antigua...")
        cursor.execute("DROP TABLE configuracion_sistema")
        
        # 4. Renombrar la nueva tabla
        cursor.execute("ALTER TABLE configuracion_sistema_new RENAME TO configuracion_sistema")
        
        # Verificar los datos
        cursor.execute("SELECT * FROM configuracion_sistema")
        config = cursor.fetchone()
        print("\nDatos actualizados:")
        print(f"ID: {config[0]}")
        print(f"Último reinicio: {config[1]} (tipo: {type(config[1]).__name__})")
        print(f"Próximo reinicio: {config[2]} (tipo: {type(config[2]).__name__})")
        
        # Confirmar los cambios
        conn.commit()
        print("\n¡Base de datos actualizada exitosamente!")
        
    except Exception as e:
        print(f"\nError al actualizar la base de datos: {e}")
        print("Se restaurará la copia de seguridad...")
        conn.rollback()
        if os.path.exists(backup_path):
            os.replace(backup_path, db_path)
            print("Se ha restaurado la copia de seguridad")
    finally:
        conn.close()

if __name__ == '__main__':
    print("=== Actualización de la estructura de la base de datos ===")
    print("Se creará una copia de seguridad antes de realizar cambios.")
    input("Presiona Enter para continuar o Ctrl+C para cancelar...")
    fix_database()
