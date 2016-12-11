# Please note that the PyCharm IDE reports the following line as a broken import, it is not.
from six.moves.urllib.parse import quote_plus
import simplejson as json
import os

class HardCoded(object):
    """Constants used throughout the application.

    All hard coded settings/data that are not actual/official configuration options for Flask or
    extensions goes here.
    """
    ADMINS = ['imp@tmiedema.com']
    DB_MODELS_IMPORTS = ('imps',)
    ENVIRONMENT = property(lambda self: self.__class__.__name__)
    _SQLALCHEMY_DATABASE_DATABASE = 'imp_flask_db'
    _SQLALCHEMY_DATABASE_HOSTNAME = 'db4free.net'
    _SQLALCHEMY_DATABASE_PASSWORD = 'Redacted'
    _SQLALCHEMY_DATABASE_USERNAME = 'imp_flask_db'


class Config(HardCoded):
    """Default Flask configuration inherited by all environments. Use this for development environments."""
    DEBUG = True
    TESTING = False
    SECRET_KEY = "i_don't_want_my_cookies_expiring_while_developing"
    MAIL_SERVER = 'smtp.localhost.test'
    MAIL_DEFAULT_SENDER = 'admin@demo.test'
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = property(lambda self: 'mysql://{u}:{p}@{h}/{d}'.format(
        d=quote_plus(self._SQLALCHEMY_DATABASE_DATABASE), h=self._SQLALCHEMY_DATABASE_HOSTNAME,
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

with open(os.path.dirname(os.path.realpath(__file__)) + '/strings.json') as fp:
    strings = json.load(fp)
