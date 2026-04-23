# setup_db.py (Modificado para horarios independientes)
from app import app, bcrypt
from database.models import db, Usuario, Peluquero, Servicio, HorarioPeluquero

def setup_inicial():
    with app.app_context():
        # ¡IMPORTANTE! Borramos y creamos para aplicar los cambios de estructura
        db.drop_all() 
        db.create_all()
        print("✅ Base de datos reseteada y tablas creadas.")

        # 1. Crear Peluqueros y sus 7 días de horario
        if not Peluquero.query.first():
            p1 = Peluquero(nombre="Peluquero A", activo=True)
            p2 = Peluquero(nombre="José Ángel", activo=True)
            db.session.add_all([p1, p2])
            db.session.flush() # Para obtener los IDs de los peluqueros

            for p in [p1, p2]:
                for dia in range(7): # 0 a 6
                    nuevo_dia = HorarioPeluquero(
                        peluquero_id=p.id,
                        dia_semana=dia,
                        trabaja=True if dia < 5 else (True if dia == 5 else False), # L-V trabaja, S trabaja, D cerrado
                        h_inicio_m="10:00", h_fin_m="14:00",
                        h_inicio_t="16:00", h_fin_t="20:00"
                    )
                    db.session.add(nuevo_dia)
            print("✅ Peluqueros y horarios base (7 días) añadidos.")

        # 2. Servicios
        servicios_base = [
            Servicio(nombre="Corte de pelo", precio=28.0),
            Servicio(nombre="Arreglo de barba", precio=26.0),
            Servicio(nombre="Corte de pelo + Arreglo barba", precio=48.0)
        ]
        db.session.add_all(servicios_base)

        # 3. Admin
        telf_admin = '633013315'
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = Usuario(nombre='Admin', telefono=telf_admin, password=hashed_pw, es_admin=True)
        db.session.add(admin)

        db.session.commit()
        print("\n🚀 Configuración profesional completada.")

if __name__ == '__main__':
    setup_inicial()