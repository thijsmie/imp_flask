from flask import render_template

from imp_flask.blueprints import home_index


@home_index.route('/')
def index():
    return render_template('home_index.html')
