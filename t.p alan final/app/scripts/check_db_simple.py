from app import app, db
from sqlalchemy import text

def check_db():
    with app.app_context():
        with db.engine.connect() as conn:
            # Ver tablas existentes
            print("\n=== Tablas en la base de datos ===")
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(tables)
            
            # Ver contenido de configuracion_sistema si existe
            if 'configuracion_sistema' in tables:
                print("\n=== Configuración del sistema ===")
                result = conn.execute(text("SELECT * FROM configuracion_sistema;"))
                config = result.first()
                if config:
                    print(f"ID: {config.id}")
                    print(f"Último reinicio: {config.ultimo_reinicio}")
                    print(f"Próximo reinicio: {config.proximo_reinicio}")
                    
                    # Calcular tiempo restante
                    from datetime import datetime
                    ahora = datetime.utcnow()
                    tiempo_restante = (config.proximo_reinicio - ahora).total_seconds()
                    print(f"Tiempo restante: {tiempo_restante} segundos")
                else:
                    print("No hay registros en configuracion_sistema")
            
            # Ver usuarios
            if 'usuario' in tables:
                print("\n=== Usuarios ===")
                result = conn.execute(text("SELECT id, nombre, email, es_admin, puntaje_semanal FROM usuario;"))
                for row in result:
                    print(f"ID: {row.id}, Nombre: {row.nombre}, Email: {row.email}, Admin: {row.es_admin}, Puntaje: {row.puntaje_semanal}")

if __name__ == '__main__':
    check_db()
