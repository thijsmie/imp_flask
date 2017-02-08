from flask import render_template, request, url_for, redirect
from flask.json import jsonify
from flask_login import login_required

from imp_flask.blueprints import relations
from imp_flask.models.imps import Relation
from imp_flask.extensions import db, validate
from imp_flask.core.auth import ensure_user_admin


@relations.route('/', defaults=dict(page=1))
@relations.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1

    pagination = Relation.query.order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_relations.html', pagination=pagination)


@relations.route('/add', defaults=dict(relation_id=0), methods=["GET", "POST"]) 
@relations.route('/edit/<int:relation_id>', methods=["GET", "POST"])
@login_required
@ensure_user_admin
def relation(relation_id):
    form = request.json
    
    if (relation_id == 0):
        relation = Relation()
        to_add = True
    else:
        relation = Relation.query.get_or_404(relation_id)
        to_add = False
    
    if request.method == "POST":
        errors = validate(form, 'relation', get_errors=True)
        if type(errors) == list:
            messages = []
            for error in errors:
                messages.append('.'.join(list(error.path)) + ": " + error.message)
            response = jsonify(messages=messages)
            response.status_code = 400
            return response
        else:
            relation.name = form['name']
            relation.email = form['email']
            relation.budget = form.get('budget', 0 if to_add else relation.budget)
            relation.send_transaction = form.get('send_transaction', True if to_add else relation.send_transaction)
            relation.send_transaction_updates = form.get('send_transaction_updates', True if to_add else relation.send_transaction_updates)
            relation.send_budget_warnings = form.get('send_budget_warnings', True if to_add else relation.send_budget_warnings)
            
            if to_add:
                db.session.add(relation)
            db.session.commit()
            
            return jsonify({})
    if to_add:
        return render_template('imp_flask_relation.html')
    else:
        return render_template('imp_flask_relation.html', relation=relation)
    

