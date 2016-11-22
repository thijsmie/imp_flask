from imp_flask.blueprints import examples_exception


@examples_exception.route('/')
def index():
    raise RuntimeError('Sample exception.')
