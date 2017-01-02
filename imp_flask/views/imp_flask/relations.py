from flask import render_template
from flask_login import login_required

from imp_flask.blueprints import relations
from imp_flask.models.imps import Relation
from imp_flask.extensions import db, validate


@relations.route('/', defaults=dict(page=1))
@relations.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1

    pagination = Relation.query.order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_relations.html', pagination=pagination)


@relations.route('/add')
@login_required
def addrelation():
    form = request.form

    if request.method == "POST":
        errors = validate(form, 'newrelation', get_errors=True)
        if type(errors) == list:
            for error in errors:
                flash.warning('.'.join(list(error.path)) + ": " + error.message)
            return redirect(url_for('.addrelation'))
        else:
            relation = Relation(form['name'], form['email'])
            #TODO, rest of this mess
    return render_template('imp_flask_newrelation.html', form=form)

