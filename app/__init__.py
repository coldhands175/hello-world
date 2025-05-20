import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config, TestConfig

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_class:
        app.config.from_object(config_class)
    elif os.environ.get('FLASK_ENV') == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
        # Ensure instance folder exists for production db
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes, models # Ensure routes and models are imported within app context

        @login_manager.user_loader
        def load_user(id):
            return models.User.query.get(int(id))

    return app
