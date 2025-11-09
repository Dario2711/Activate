from app import app, db
from models import Usuario

def update_database():
    with app.app_context():
        # Crear todas las tablas (esto actualizará el esquema)
        db.create_all()
        
        # Verificar si ya existe un usuario administrador
        admin_exists = Usuario.query.filter_by(es_admin=True).first()
        
        if not admin_exists:
            # Si no hay administradores, hacer que el primer usuario sea administrador
            first_user = Usuario.query.first()
            if first_user:
                first_user.es_admin = True
                db.session.commit()
                print("Se ha asignado el primer usuario como administrador.")
            else:
                print("No hay usuarios en la base de datos.")
        
        print("Base de datos actualizada correctamente.")

if __name__ == '__main__':
    update_database()
