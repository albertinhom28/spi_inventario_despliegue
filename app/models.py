from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(100), nullable=False)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol           = db.Column(db.String(20), nullable=False, default='tecnico')
    activo        = db.Column(db.Boolean, nullable=False, default=True)
    created_at    = db.Column(db.DateTime, nullable=False, default=datetime.now)

    mantenimientos_registrados = db.relationship('Mantenimiento', backref='registrado_por', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def es_admin(self):
        return self.rol == 'admin'

    def es_tecnico(self):
        return self.rol in ('admin', 'tecnico')


class Equipo(db.Model):
    __tablename__ = 'equipos'

    id                = db.Column(db.Integer, primary_key=True)
    codigo            = db.Column(db.String(20), unique=True, nullable=False)
    marca             = db.Column(db.String(50), nullable=False)
    modelo            = db.Column(db.String(100), nullable=False)
    serial            = db.Column(db.String(100))
    departamento      = db.Column(db.String(100), nullable=False)
    tipo_disco        = db.Column(db.String(20), nullable=False)
    capacidad_disco   = db.Column(db.Integer)
    ram_gb            = db.Column(db.Integer, nullable=False)
    sistema_operativo = db.Column(db.String(50))
    estado            = db.Column(db.String(20), nullable=False, default='operativo')
    fecha_registro    = db.Column(db.Date, nullable=False, default=date.today)
    created_at        = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_by        = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    mantenimientos = db.relationship('Mantenimiento', backref='equipo',
                                     lazy=True, cascade='all, delete-orphan')
    alerta         = db.relationship('Alerta', backref='equipo',
                                     uselist=False, cascade='all, delete-orphan')

    def ultimo_mantenimiento(self):
        m = Mantenimiento.query.filter_by(equipo_id=self.id)\
                               .order_by(Mantenimiento.fecha.desc()).first()
        return m.fecha if m else None

    def dias_sin_mantenimiento(self):
        ultima = self.ultimo_mantenimiento()
        referencia = ultima if ultima else self.fecha_registro
        return (date.today() - referencia).days

    def nivel_alerta(self):
        dias = self.dias_sin_mantenimiento()
        if dias >= 90:
            return 'vencido'
        elif dias >= 75:
            return 'pendiente'
        elif dias >= 60:
            return 'proximo'
        return None


class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'

    id                  = db.Column(db.Integer, primary_key=True)
    equipo_id           = db.Column(db.Integer, db.ForeignKey('equipos.id',
                                    ondelete='CASCADE'), nullable=False)
    fecha               = db.Column(db.Date, nullable=False)
    tipo                = db.Column(db.String(20), nullable=False)
    actividades         = db.Column(db.Text, nullable=False)
    tecnico_responsable = db.Column(db.String(100), nullable=False)
    observaciones       = db.Column(db.Text)
    created_at          = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_by          = db.Column(db.Integer, db.ForeignKey('usuarios.id'))


class Alerta(db.Model):
    __tablename__ = 'alertas'

    id             = db.Column(db.Integer, primary_key=True)
    equipo_id      = db.Column(db.Integer, db.ForeignKey('equipos.id',
                                ondelete='CASCADE'), unique=True, nullable=False)
    dias_sin_mtto  = db.Column(db.Integer, nullable=False)
    nivel          = db.Column(db.String(20), nullable=False)
    fecha_generada = db.Column(db.DateTime, nullable=False, default=datetime.now)