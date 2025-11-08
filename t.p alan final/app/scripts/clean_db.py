import os
import shutil
from app import app, db

def clean_database():
    # Ruta a la base de datos
    db_path = 'instance/usuarios.db'
    
    # Cerrar todas las conexiones a la base de datos
    db.session.close()
    
    # Eliminar la base de datos si existe
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Base de datos eliminada: {db_path}")
        except Exception as e:
            print(f"No se pudo eliminar la base de datos: {e}")
            # Si no se puede eliminar, intentar renombrar
            try:
                backup_path = f"{db_path}.backup"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(db_path, backup_path)
                print(f"Base de datos renombrada a: {backup_path}")
            except Exception as e2:
                print(f"No se pudo renombrar la base de datos: {e2}")
                return False
    
    # Crear el directorio si no existe
    os.makedirs('instance', exist_ok=True)
    
    # Crear una nueva base de datos con las tablas actualizadas
    with app.app_context():
        try:
            db.create_all()
            print("Nueva base de datos creada exitosamente")
            return True
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
            return False

if __name__ == '__main__':
    print("=== Limpieza de la base de datos ===")
    if clean_database():
        print("\n✅ ¡Base de datos limpiada y recreada exitosamente!")
        print("\nAhora puedes iniciar la aplicación con:")
        print("python app.py")
    else:
        print("\n❌ Error al limpiar la base de datos.")
        print("Por favor, cierra todos los programas que puedan estar usando la base de datos")
        print("y vuelve a intentarlo, o reinicia tu computadora.")
