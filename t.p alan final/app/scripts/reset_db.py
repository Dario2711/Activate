import os
import time
import sqlite3
from app import app, db

def reset_database():
    with app.app_context():
        # Cerrar conexiones existentes
        db.session.close_all()
        
        # Esperar un momento para asegurar que se cierren las conexiones
        time.sleep(1)
        
        # Ruta a la base de datos
        db_path = os.path.join('instance', 'usuarios.db')
        
        # Eliminar la base de datos si existe
        if os.path.exists(db_path):
            try:
                # Forzar la eliminación del archivo
                os.unlink(db_path)
                print(f"Base de datos eliminada: {db_path}")
            except Exception as e:
                print(f"Error al eliminar la base de datos: {e}")
                # Si no se puede eliminar, intentar renombrar
                try:
                    os.rename(db_path, f"{db_path}.old")
                    print(f"Base de datos renombrada a {db_path}.old")
                except Exception as e2:
                    print(f"Error al renombrar la base de datos: {e2}")
                    return False
    
    # Crear el directorio si no existe
    os.makedirs('instance', exist_ok=True)
    
    # Crear una nueva base de datos
    with app.app_context():
        try:
            db.create_all()
            print("Nueva base de datos creada exitosamente")
            return True
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
            return False

if __name__ == '__main__':
    if reset_database():
        print("\n¡Base de datos reiniciada exitosamente!")
        print("Ahora puedes iniciar la aplicación con: python app.py")
    else:
        print("\nError al reiniciar la base de datos. Intenta cerrar todos los programas que puedan estar usando la base de datos.")
        print("Si el problema persiste, reinicia tu computadora y vuelve a intentarlo.")
