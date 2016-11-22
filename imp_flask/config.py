# Please note that the PyCharm IDE reports the following line as a broken import, it is not.
from six.moves.urllib.parse import quote_plus


class HardCoded(object):
    """Constants used throughout the application.

    All hard coded settings/data that are not actual/official configuration options for Flask or
    extensions goes here.
    """
    ADMINS = ['imp@tmiedema.com']
    DB_MODELS_IMPORTS = ('imp',)
    ENVIRONMENT = property(lambda self: self.__class__.__name__)
    MAIL_EXCEPTION_THROTTLE = 24 * 60 * 60
    _SQLALCHEMY_DATABASE_DATABASE = 'imp_flask'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'localhost'
    _SQLALCHEMY_DATABASE_PASSWORD = 'impp@ssword'
    _SQLALCHEMY_DATABASE_USERNAME = 'impservice'


class Config(HardCoded):
    """Default Flask configuration inherited by all environments. Use this for development environments."""
    DEBUG = True
    TESTING = False
    SECRET_KEY = "i_don't_want_my_cookies_expiring_while_developing"
    MAIL_SERVER = 'smtp.localhost.test'
    MAIL_DEFAULT_SENDER = 'admin@demo.test'
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = property(lambda self: 'mysql://{u}:{p}@{h}/{d}'.format(
        d=quote_plus(self._SQLALCHEMY_DATABASE_DATABASE), h=quote_plus(self._SQLALCHEMY_DATABASE_HOSTNAME),
        p=quote_plus(self._SQLALCHEMY_DATABASE_PASSWORD), u=quote_plus(self._SQLALCHEMY_DATABASE_USERNAME)
    ))


class Testing(Config):
    TESTING = True
    _SQLALCHEMY_DATABASE_DATABASE = 'imp_flask_testing'


class Production(Config):
    DEBUG = False
    SECRET_KEY = None  # To be overwritten by a YAML file.
    ADMINS = ['imp@tmiedema.com']
    MAIL_SUPPRESS_SEND = False
    STATICS_MINIFY = True
