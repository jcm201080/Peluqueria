from app import app, bcrypt
from database.models import db, Usuario, Peluquero, Servicio, Configuracion

def setup_inicial():
    with app.app_context():
        # 1. Crear las tablas
        db.create_all()
        print("✅ Tablas verificadas/creadas.")

        # 2. Crear Peluqueros
        if not Peluquero.query.first():
            db.session.add_all([
                Peluquero(nombre="Peluquero A", activo=True),
                Peluquero(nombre="Peluquero B", activo=True)
            ])
            print("✅ Peluqueros iniciales añadidos.")

        # 3. Crear Servicios por defecto (tus precios del HTML)
        if not Servicio.query.first():
            servicios_base = [
                Servicio(nombre="Corte de pelo", precio=28.0),
                Servicio(nombre="Arreglo de barba", precio=26.0),
                Servicio(nombre="Corte de pelo + Arreglo barba", precio=48.0),
                Servicio(nombre="Corte de niño hasta 6 años", precio=18.0),
                Servicio(nombre="Corte de niño hasta 12 años", precio=21.0)
            ]
            db.session.add_all(servicios_base)
            print("✅ Servicios iniciales añadidos.")

        # 4. Crear Configuración de Horarios por defecto
        if not Configuracion.query.first():
            horario = Configuracion(
                h_inicio_manana="10:00", h_fin_manana="14:00",
                h_inicio_tarde="18:00", h_fin_tarde="20:00"
            )
            db.session.add(horario)
            print("✅ Horarios configurados por defecto.")

        # 5. Administrador
        telf_admin = '633013315'
        pass_admin = 'admin123'
        admin = Usuario.query.filter_by(telefono=telf_admin).first()
        hashed_pw = bcrypt.generate_password_hash(pass_admin).decode('utf-8')

        if not admin:
            nuevo_admin = Usuario(nombre='Administrador Jefe', telefono=telf_admin, password=hashed_pw, es_admin=True)
            db.session.add(nuevo_admin)
            print(f"✅ Admin creado: {telf_admin}")
        else:
            admin.es_admin = True
            admin.password = hashed_pw

        db.session.commit()
        print("\n🚀 Todo listo.")

if __name__ == '__main__':
    setup_inicial()