from flask import render_template, abort
from flask_login import login_required

from imp_flask.blueprints import mods
from imp_flask.models.imps import Mod


@mods.route('/', defaults=dict(page=1))
@mods.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1
    pagination = Mod.query.order_by('id').paginate(page, per_page=25, error_out=False)
    return render_template('imp_flask_mods.html', pagination=pagination)
    
    
@mods.route('/details/<int:mod_id>')
@login_required
def details(mod_id):
    mod = Mod.query.get(mod_id)
    if mod is None:
        return abort(404)
        
    return render_template('imp_flask_mod_details.html', mod=mod)
