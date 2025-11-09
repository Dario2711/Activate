from app import app, db
import os

# Eliminar la base de datos existente si existe
if os.path.exists('instance/usuarios.db'):
    try:
        os.remove('instance/usuarios.db')
        print("Base de datos antigua eliminada")
    except Exception as e:
        print(f"Error al eliminar la base de datos: {e}")

# Crear todas las tablas
with app.app_context():
    db.create_all()
    print("Base de datos creada exitosamente con la estructura actualizada")
