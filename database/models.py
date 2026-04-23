from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    citas = db.relationship('Cita', backref='cliente_rel', lazy=True)

class Peluquero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    # Relaciones
    horarios = db.relationship('HorarioPeluquero', backref='peluquero', lazy=True, cascade="all, delete-orphan")
    excepciones = db.relationship('ExcepcionHorario', backref='peluquero', lazy=True)
    citas = db.relationship('Cita', backref='peluquero_rel', lazy=True)

class HorarioPeluquero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    peluquero_id = db.Column(db.Integer, db.ForeignKey('peluquero.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False) # 0=Lunes, 6=Domingo
    trabaja = db.Column(db.Boolean, default=True)
    h_inicio_m = db.Column(db.String(5), default="10:00")
    h_fin_m = db.Column(db.String(5), default="14:00")
    h_inicio_t = db.Column(db.String(5), default="16:00")
    h_fin_t = db.Column(db.String(5), default="20:00")

class ExcepcionHorario(db.Model):
    """ Para festivos, vacaciones o días que no se trabaja """
    id = db.Column(db.Integer, primary_key=True)
    peluquero_id = db.Column(db.Integer, db.ForeignKey('peluquero.id'), nullable=True) # NULL significa festivo para todos
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(100)) # Ej: "Navidad", "Vacaciones Paco"
    es_cerrado = db.Column(db.Boolean, default=True)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    servicio = db.Column(db.String(100))
    peluquero_id = db.Column(db.Integer, db.ForeignKey('peluquero.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    nombre_invitado = db.Column(db.String(100), nullable=True) 
    telefono_cliente = db.Column(db.String(20), nullable=False)

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    duracion = db.Column(db.Integer, default=30) 

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    h_inicio_manana = db.Column(db.String(5), default="10:00")
    h_fin_manana = db.Column(db.String(5), default="14:00")
    h_inicio_tarde = db.Column(db.String(5), default="17:00")
    h_fin_tarde = db.Column(db.String(5), default="21:30")