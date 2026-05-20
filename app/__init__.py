from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models import db, User

bcrypt = Bcrypt()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'pathflow-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pathflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Pehle login karo!'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app