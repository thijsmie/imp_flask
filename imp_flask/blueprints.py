"""All Flask blueprints for the entire application.

All blueprints for all views go here. They shall be imported by the views themselves and by application.py. Blueprint
URL paths are defined here as well.
"""

from flask import Blueprint


def blueprint_factory(partial_module_string, url_prefix):
    """Generates blueprint objects for view modules.

    Positional arguments:
    partial_module_string -- string representing a view module without the absolute path (e.g. 'home.index' for
        imp_flask.views.home.index).
    url_prefix -- URL prefix passed to the blueprint.

    Returns:
    Blueprint instance for a view module.
    """
    name = partial_module_string
    import_name = 'imp_flask.views.{}'.format(partial_module_string)
    template_folder = 'templates'
    blueprint = Blueprint(name, import_name, template_folder=template_folder, url_prefix=url_prefix)
    return blueprint


home_index = blueprint_factory('home.index', '')
relations = blueprint_factory('imp_flask.relations', '/relations')
transactions = blueprint_factory('imp_flask.transactions', '/transactions')
products = blueprint_factory('imp_flask.products', '/products')
mods = blueprint_factory('imp_flask.mods', '/mods')
#pos = blueprint_factory('imp_flask.pos', '/pos')
#conscribo = blueprint_factory('imp_flask.conscribo', '/conscribo')
#settings = blueprint_factory('imp_flask.settings', '/settings')

all_blueprints = [home_index, products, relations, transactions, mods]  # conscribo, settings,)
