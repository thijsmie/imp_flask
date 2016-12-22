"""Make paths importable app-wide"""

import os

import imp_flask as app_root


APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))
TEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'templates')
TEXTEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'textemplates')
TEXSTATIC_FOLDER = os.path.join(APP_ROOT_FOLDER, 'texstatic')
STATIC_FOLDER = os.path.join(APP_ROOT_FOLDER, 'static')
VALIDATORS_FOLDER = os.path.join(APP_ROOT_FOLDER, 'validators')
