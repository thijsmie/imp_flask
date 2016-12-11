"""Holds the create_app() Flask application factory. More information in create_app() docstring."""

from importlib import import_module
import os

from flask import Flask
from flask_statics import Statics
from yaml import load

import imp_flask as app_root
from imp_flask.blueprints import all_blueprints
from imp_flask.extensions import db, mail

APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))
TEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'templates')
TEXTEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'textemplates')
STATIC_FOLDER = os.path.join(APP_ROOT_FOLDER, 'static')


def get_config(config_class_string, yaml_files=None):
    """Load the Flask config from a class.

    Positional arguments:
    config_class_string -- string representation of a configuration class that will be loaded (e.g.
        'imp_flask.config.Production').
    yaml_files -- List of YAML files to load. This is for testing, leave None in dev/production.

    Returns:
    A class object to be fed into app.config.from_object().
    """
    config_module, config_class = config_class_string.rsplit('.', 1)
    config_class_object = getattr(import_module(config_module), config_class)
    config_obj = config_class_object()

    # Expand some options.
    db_fmt = 'imp_flask.models.{}'
    if getattr(config_obj, 'DB_MODELS_IMPORTS', False):
        config_obj.DB_MODELS_IMPORTS = [db_fmt.format(m) for m in config_obj.DB_MODELS_IMPORTS]

    # Load additional configuration settings.
    yaml_files = yaml_files or [f for f in [
        os.path.join('/', 'etc', 'imp_flask', 'config.yml'),
        os.path.abspath(os.path.join(APP_ROOT_FOLDER, '..', 'config.yml')),
        os.path.join(APP_ROOT_FOLDER, 'config.yml'),
    ] if os.path.exists(f)]
    additional_dict = dict()
    for y in yaml_files:
        with open(y) as f:
            additional_dict.update(load(f.read()))

    # Merge the rest into the Flask app config.
    for key, value in additional_dict.items():
        setattr(config_obj, key, value)

    return config_obj


def create_app(config_obj, no_sql=False):
    """Flask application factory. Initializes and returns the Flask application.

    Blueprints are registered in here.

    Modeled after: http://flask.pocoo.org/docs/patterns/appfactories/

    Positional arguments:
    config_obj -- configuration object to load into app.config.

    Keyword arguments:
    no_sql -- does not run init_app() for the SQLAlchemy instance.

    Returns:
    The initialized Flask application.
    """
    # Initialize app. Flatten config_obj to dictionary (resolve properties).
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
    config_dict = dict([(k, getattr(config_obj, k)) for k in dir(config_obj) if not k.startswith('_')])
    app.config.update(config_dict)

    # Import DB models.
    with app.app_context():
        for module in app.config.get('DB_MODELS_IMPORTS', list()):
            import_module(module)

    # Setup redirects and register blueprints.
    app.add_url_rule('/favicon.ico', 'favicon', lambda: app.send_static_file('favicon.ico'))
    for bp in all_blueprints:
        import_module(bp.import_name)
        app.register_blueprint(bp)

    # Initialize extensions/add-ons/plugins.
    if not no_sql:
        db.init_app(app)
    Statics(app)  # Enable Flask-Statics-Helper features.
    mail.init_app(app)

    # Activate middleware.
    with app.app_context():
        import_module('imp_flask.middleware')

    # Return the application instance.
    return app
