from app import app, db
from datetime import datetime, timedelta

def check_database():
    with app.app_context():
        # Verificar tablas
        inspector = db.inspect(db.engine)
        print("\n=== Tablas en la base de datos ===")
        tables = inspector.get_table_names()
        print(tables)
        
        # Verificar configuración del sistema
        print("\n=== Configuración del sistema ===")
        if 'configuracion_sistema' in tables:
            config = db.session.query(db.metadata.tables['configuracion_sistema']).first()
            if config:
                print(f"ID: {config.id}")
                print(f"Último reinicio: {config.ultimo_reinicio}")
                print(f"Próximo reinicio: {config.proximo_reinicio}")
                
                # Calcular tiempo restante
                ahora = datetime.utcnow()
                tiempo_restante = (config.proximo_reinicio - ahora).total_seconds()
                print(f"Tiempo restante: {tiempo_restante} segundos")
                
                # Verificar usuarios
                print("\n=== Usuarios ===")
                if 'usuario' in tables:
                    usuarios = db.session.execute(db.text("SELECT id, nombre, puntaje_semanal FROM usuario")).fetchall()
                    for user in usuarios:
                        print(f"ID: {user[0]}, Nombre: {user[1]}, Puntaje semanal: {user[2]}")
            else:
                print("No hay configuración del sistema")
                
                # Crear configuración si no existe
                print("\nCreando configuración inicial...")
                try:
                    from models import ConfiguracionSistema
                    nueva_config = ConfiguracionSistema(
                        ultimo_reinicio=datetime.utcnow(),
                        proximo_reinicio=datetime.utcnow() + timedelta(days=7)
                    )
                    db.session.add(nueva_config)
                    db.session.commit()
                    print("Configuración creada exitosamente")
                except Exception as e:
                    print(f"Error al crear configuración: {e}")
                    db.session.rollback()
        else:
            print("La tabla configuracion_sistema no existe")

if __name__ == '__main__':
    check_database()
