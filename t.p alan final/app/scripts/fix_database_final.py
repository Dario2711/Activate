import os
import sqlite3
from datetime import datetime, timedelta

def fix_database():
    # Ruta a la base de datos
    db_path = os.path.join('instance', 'usuarios.db')
    backup_path = os.path.join('instance', 'usuarios_backup_final.db')
    
    print("=== Actualización de la estructura de la base de datos ===")
    print(f"Base de datos: {os.path.abspath(db_path)}")
    
    # Hacer una copia de seguridad
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"\n✅ Se ha creado una copia de seguridad en: {os.path.abspath(backup_path)}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar la estructura actual
        print("\n🔍 Verificando estructura actual...")
        cursor.execute("PRAGMA table_info(configuracion_sistema)")
        columns = cursor.fetchall()
        print("\nEstructura actual de la tabla configuracion_sistema:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # 2. Obtener los datos actuales
        cursor.execute("SELECT * FROM configuracion_sistema")
        config_data = cursor.fetchone()
        
        if config_data:
            print("\n📊 Datos actuales:")
            print(f"ID: {config_data[0]}")
            print(f"Último reinicio: {config_data[1]} (tipo: {type(config_data[1]).__name__})")
            print(f"Próximo reinicio: {config_data[2]} (tipo: {type(config_data[2]).__name__})")
        
        # 3. Crear tabla temporal con estructura correcta
        print("\n🔄 Creando nueva estructura...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_sistema_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ultimo_reinicio TIMESTAMP NOT NULL,
            proximo_reinicio TIMESTAMP NOT NULL
        )
        """)
        
        # 4. Convertir y copiar los datos
        if config_data:
            print("\n📥 Copiando datos existentes con formato corregido...")
            
            # Función para convertir fechas
            def convert_date(date_str):
                try:
                    # Si ya es un datetime, devolverlo directamente
                    if isinstance(date_str, datetime):
                        return date_str
                    
                    # Intentar convertir desde diferentes formatos
                    for fmt in (
                        '%Y-%m-%d %H:%M:%S.%f',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d'
                    ):
                        try:
                            return datetime.strptime(str(date_str), fmt)
                        except ValueError:
                            continue
                    
                    # Si no se pudo convertir, usar la fecha actual
                    return datetime.utcnow()
                except Exception as e:
                    print(f"⚠️  Error al convertir fecha '{date_str}': {e}")
                    return datetime.utcnow()
            
            # Convertir fechas
            ultimo_reinicio = convert_date(config_data[1])
            proximo_reinicio = convert_date(config_data[2])
            
            # Insertar datos convertidos
            cursor.execute("""
                INSERT INTO configuracion_sistema_new 
                (id, ultimo_reinicio, proximo_reinicio)
                VALUES (?, ?, ?)
            """, (
                config_data[0],
                ultimo_reinicio.isoformat(),
                proximo_reinicio.isoformat()
            ))
        else:
            # Si no hay datos, insertar valores por defecto
            ahora = datetime.utcnow()
            cursor.execute("""
                INSERT INTO configuracion_sistema_new 
                (ultimo_reinicio, proximo_reinicio)
                VALUES (?, ?)
            """, (
                ahora.isoformat(),
                (ahora + timedelta(days=7)).isoformat()
            ))
        
        # 5. Reemplazar la tabla antigua
        print("\n🔄 Reemplazando la tabla antigua...")
        cursor.execute("DROP TABLE configuracion_sistema")
        cursor.execute("ALTER TABLE configuracion_sistema_new RENAME TO configuracion_sistema")
        
        # 6. Verificar los cambios
        cursor.execute("SELECT * FROM configuracion_sistema")
        new_config = cursor.fetchone()
        
        print("\n✅ Base de datos actualizada exitosamente!")
        print("\n📋 Nuevos datos:")
        print(f"ID: {new_config[0]}")
        print(f"Último reinicio: {new_config[1]}")
        print(f"Próximo reinicio: {new_config[2]}")
        
        # Confirmar cambios
        conn.commit()
        
    except Exception as e:
        print(f"\n❌ Error durante la actualización: {str(e)}")
        print("\n⚠️  Se restaurará la copia de seguridad...")
        if os.path.exists(backup_path):
            os.replace(backup_path, db_path)
            print("✅ Se ha restaurado la copia de seguridad")
    finally:
        if 'conn' in locals():
            conn.close()
        print("\nProceso finalizado.")

if __name__ == '__main__':
    print("=== Herramienta de reparación de base de datos ===")
    print("Este script actualizará la estructura de la base de datos para corregir problemas con el temporizador.")
    print("Se creará una copia de seguridad antes de realizar cambios.")
    
    confirm = input("\n¿Deseas continuar? (s/n): ")
    if confirm.lower() == 's':
        fix_database()
    else:
        print("\nOperación cancelada por el usuario.")
