import os
import sys
from app import app, db

def main():
    with app.app_context():
        # Eliminar todas las tablas existentes
        db.drop_all()
        print("Tablas existentes eliminadas")
        
        # Crear todas las tablas con la estructura actual
        db.create_all()
        print("Nuevas tablas creadas exitosamente")
        
        print("\n¡Base de datos reiniciada correctamente!")
        print("Ahora puedes iniciar la aplicación con: python app.py")

if __name__ == "__main__":
    # Verificar si la base de datos existe
    if os.path.exists('instance/usuarios.db'):
        print("Advertencia: La base de datos ya existe.")
        respuesta = input("¿Deseas eliminar la base de datos existente? (s/n): ")
        if respuesta.lower() == 's':
            main()
        else:
            print("Operación cancelada.")
    else:
        main()
