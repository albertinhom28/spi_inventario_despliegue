from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config
from app.models import db, Usuario

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Cargar usuario desde sesión
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from app.auth.routes import auth_bp
    from app.inventario.routes import inventario_bp
    from app.mantenimientos.routes import mantenimientos_bp
    from app.alertas.routes import alertas_bp
    from app.reportes.routes import reportes_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(mantenimientos_bp)
    app.register_blueprint(alertas_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(admin_bp)

    return app