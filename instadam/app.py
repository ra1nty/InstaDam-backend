import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import app_config
from flask_jwt_extended import JWTManager

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
    from . import project
    app.register_blueprint(auth.bp)

    return app