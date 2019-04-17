"""Config for the server
"""

import os

DATABASE_USERNAME = 'postgres'
DATABASE_HOSTNAME = 'postgres'
DATABASE_PASSWORD = ''
DATABASE_NAME = 'instadam'
FLASK_SECRETE_KEY = ''
if '_DB_USERNAME' in os.environ and os.environ['_DB_USERNAME'] is not None:
    DATABASE_USERNAME = os.environ['_DB_USERNAME']
if '_DB_PASSWORD' in os.environ and os.environ['_DB_PASSWORD'] is not None:
    DATABASE_PASSWORD = os.environ['_DB_PASSWORD']
if '_SECRETE_KEY' in os.environ and os.environ['_SECRETE_KEY'] is not None:
    FLASK_SECRETE_KEY = os.environ['_SECRETE_KEY']
if '_DB_HOSTNAME' in os.environ and os.environ['_DB_HOSTNAME'] is not None:
    DATABASE_HOSTNAME = os.environ['_DB_HOSTNAME']
if '_DB_NAME' in os.environ and os.environ['_DB_NAME'] is not None:
    DATABASE_NAME = os.environ['_DB_NAME']

INSTADAM_STORAGE = 'static-dir'
if ('INSTADAM_STORAGE' in os.environ
        and os.environ['INSTADAM_STORAGE'] is not None):
    INSTADAM_STORAGE = os.environ['INSTADAM_STORAGE']
INSTADAM_STORAGE_ROOT_URL = 'static'
if ('INSTADAM_STORAGE_ROOT_URL' in os.environ
        and os.environ['INSTADAM_STORAGE_ROOT_URL'] is not None):
    INSTADAM_STORAGE_ROOT_URL = os.environ['INSTADAM_STORAGE_ROOT_URL']


class Config(object):
    """Some default config
    """
    DEVELOPMENT = False
    TESTING = False

    MAIL_SERVER = 'smtp.localhost.test'
    MAIL_DEFAULT_SENDER = 'admin@demo.test'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    JWT_ACCESS_TOKEN_EXPIRES = False

    STATIC_STORAGE_DIR = INSTADAM_STORAGE
    STATIC_STORAGE_URL = INSTADAM_STORAGE_ROOT_URL


class Development(Config):
    """Development config
    """
    DEVELOPMENT = True

    SECRET_KEY = 'Some really random string'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In-memory sqlite db
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Production(Config):
    """Production config
    """
    SECRET_KEY = FLASK_SECRETE_KEY
    _SQLALCHEMY_DATABASE_DATABASE = DATABASE_NAME
    _SQLALCHEMY_DATABASE_HOSTNAME = DATABASE_HOSTNAME
    _SQLALCHEMY_DATABASE_PASSWORD = DATABASE_PASSWORD
    _SQLALCHEMY_DATABASE_USERNAME = DATABASE_USERNAME
    SQLALCHEMY_DATABASE_URI = 'postgres://{u}:{p}@{h}/{d}'.format(
        d=_SQLALCHEMY_DATABASE_DATABASE,
        h=_SQLALCHEMY_DATABASE_HOSTNAME,
        p=_SQLALCHEMY_DATABASE_PASSWORD,
        u=_SQLALCHEMY_DATABASE_USERNAME)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Testing(Config):
    """Testing config
    """
    SECRET_KEY = 'Some really random string'
    _SQLALCHEMY_DATABASE_DATABASE = 'travis_ci_test'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = DATABASE_PASSWORD
    _SQLALCHEMY_DATABASE_USERNAME = DATABASE_USERNAME
    SQLALCHEMY_DATABASE_URI = 'postgres://{u}:{p}@{h}/{d}'.format(
        d=_SQLALCHEMY_DATABASE_DATABASE,
        h=_SQLALCHEMY_DATABASE_HOSTNAME,
        p=_SQLALCHEMY_DATABASE_PASSWORD,
        u=_SQLALCHEMY_DATABASE_USERNAME)
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app_config = {
    'development': Development,
    'production': Production,
    'testing': Testing
}
