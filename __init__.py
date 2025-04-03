from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TuClaveSecretaAqui'  # ¡Reemplaza esto con una clave secreta segura!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from .models import User  # Importar aquí para evitar importación circular en load_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import routes, auth_routes, admin_routes, seller_routes

app.register_blueprint(auth_routes.auth_bp, url_prefix='/auth')
app.register_blueprint(admin_routes.admin_bp, url_prefix='/admin')
app.register_blueprint(seller_routes.seller_bp, url_prefix='/seller')