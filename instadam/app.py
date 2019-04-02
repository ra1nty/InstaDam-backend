import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from .config import app_config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(mode='development'):
    """
    create and configure the app in specific mode

    Args:
        mode: A string indicate the mode of the application
            one of 'development', 'production', 'testing'

    Returns:
        The initialized Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[mode])
    db.init_app(app)
    jwt.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import error_handlers
    app.register_blueprint(error_handlers.bp)

    from . import image
    app.register_blueprint(image.bp)

    from . import project
    app.register_blueprint(project.bp)

    from . import annotation
    app.register_blueprint(annotation.bp)

    from . import search_users
    app.register_blueprint(search_users.bp)

    from . import user
    app.register_blueprint(user.bp)

    if not os.path.isdir(app.config['STATIC_STORAGE_DIR']):
        os.mkdir(app.config['STATIC_STORAGE_DIR'])

    return app
