from app import app, db
import os

def recreate_database():
    # Eliminar el archivo de la base de datos si existe
    db_path = 'instance/usuarios.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Base de datos antigua eliminada")
        except Exception as e:
            print(f"Error al eliminar la base de datos: {e}")
            return False
    
    # Crear la carpeta instance si no existe
    os.makedirs('instance', exist_ok=True)
    
    # Crear todas las tablas
    with app.app_context():
        try:
            db.create_all()
            print("Base de datos recreada exitosamente")
            return True
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
            return False

if __name__ == '__main__':
    print("=== RECREACIÓN DE LA BASE DE DATOS ===")
    if recreate_database():
        print("\n✅ ¡Base de datos recreada exitosamente!")
        print("\nAhora puedes iniciar la aplicación con:")
        print("python app.py")
    else:
        print("\n❌ Error al recrear la base de datos.")
        print("Por favor, cierra todos los programas que puedan estar usando la base de datos")
        print("y vuelve a intentarlo, o reinicia tu computadora.")
