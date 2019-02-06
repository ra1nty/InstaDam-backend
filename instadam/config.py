class Config(object):
    # Some default config
    DEVELOPMENT = False
    TESTING = False

    MAIL_SERVER = 'smtp.localhost.test'
    MAIL_DEFAULT_SENDER = 'admin@demo.test'

class Development(Config):
    """
    Development config
    """
    DEVELOPMENT = True

    SECRET_KEY = "Some really random string"
    SQLALCHEMY_DATABASE_URI = 'sqlite://' # In-memory sqlite db
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Production(Config):
    """
    Production config
    """
    SECRET_KEY = ""
    _SQLALCHEMY_DATABASE_DATABASE = ''
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = ''
    _SQLALCHEMY_DATABASE_USERNAME = 'postgres'
    SQLALCHEMY_DATABASE_URI = 'postgres://{u}:{p}@{h}/{d}'.format(
        d=_SQLALCHEMY_DATABASE_DATABASE, h=_SQLALCHEMY_DATABASE_HOSTNAME,
        p=_SQLALCHEMY_DATABASE_PASSWORD, u=_SQLALCHEMY_DATABASE_USERNAME
    )
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Testing(Config):
    """
    Testing config
    """
    TESTING = True

    SECRET_KEY = ""
    _SQLALCHEMY_DATABASE_DATABASE = 'travis_ci_test'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = ''
    _SQLALCHEMY_DATABASE_USERNAME = 'postgres'
    SQLALCHEMY_DATABASE_URI = 'postgres://{u}:{p}@{h}/{d}'.format(
        d=_SQLALCHEMY_DATABASE_DATABASE, h=_SQLALCHEMY_DATABASE_HOSTNAME,
        p=_SQLALCHEMY_DATABASE_PASSWORD, u=_SQLALCHEMY_DATABASE_USERNAME
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app_config = {
    'development' : Development,
    'production' : Production,
    'testing' : Testing
}