import os
from app import app, db

def reset_database():
    # Eliminar el archivo de la base de datos si existe
    db_path = 'instance/usuarios.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Base de datos eliminada: {db_path}")
        except Exception as e:
            print(f"Error al eliminar la base de datos: {e}")
            return False
    
    # Asegurarse de que el directorio instance existe
    os.makedirs('instance', exist_ok=True)
    
    # Crear todas las tablas
    with app.app_context():
        try:
            db.create_all()
            print("Base de datos creada exitosamente con la estructura actualizada")
            return True
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
            return False

if __name__ == '__main__':
    print("=== REINICIANDO LA BASE DE DATOS ===")
    if reset_database():
        print("\n¡Base de datos reiniciada exitosamente!")
        print("Ahora puedes iniciar la aplicación con: python app.py")
    else:
        print("\n❌ Error al reiniciar la base de datos.")
        print("Por favor, cierra todos los programas que puedan estar usando la base de datos")
        print("y vuelve a intentarlo, o reinicia tu computadora.")
