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
    # Horarios (simplificado: el mismo para todos sus días laborables, o puedes ampliarlo)
    h_inicio_manana = db.Column(db.String(5), default="10:00")
    h_fin_manana = db.Column(db.String(5), default="14:00")
    h_inicio_tarde = db.Column(db.String(5), default="18:00")
    h_fin_tarde = db.Column(db.String(5), default="20:00")
    # Días laborables (ej: "0,1,2,3,4,5" para Lunes a Sábado)
    dias_laborables = db.Column(db.String(20), default="0,1,2,3,4,5")

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    servicio = db.Column(db.String(100))
    peluquero_id = db.Column(db.Integer, db.ForeignKey('peluquero.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    nombre_invitado = db.Column(db.String(100), nullable=True) 
    telefono_cliente = db.Column(db.String(20), nullable=False)

# --- NUEVAS TABLAS ---

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    duracion = db.Column(db.Integer, default=30) # minutos por si algún servicio tarda más

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Guardamos los horarios como strings "HH:MM" para facilitar el manejo en el admin
    h_inicio_manana = db.Column(db.String(5), default="10:00")
    h_fin_manana = db.Column(db.String(5), default="14:00")
    h_inicio_tarde = db.Column(db.String(5), default="18:00")
    h_fin_tarde = db.Column(db.String(5), default="20:00")