from flask import render_template, redirect
from flask_login import login_required

from imp_flask.blueprints import transactions
from imp_flask.models.imps import Transaction
from imp_flask.core.auth import ensure_user_relation


@transactions.route('/', defaults=dict(page=1))
@transactions.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1

    pagination = Transaction.query.order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_transactions.html', showrelation=True, pagination=pagination)


@transactions.route('/relation/<int:relation_id>', defaults=dict(page=1))
@transactions.route('/relation/<int:relation_id>/page/<int:page>')
@login_required
@ensure_user_relation
def showrelation(relation_id, page):
    if page <= 0:
        page = 1

    pagination = Transaction.query.filter(Transaction.relation_id == relation_id).order_by('eventnumber').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_transactions.html', showrelation=False, pagination=pagination)


@transactions.route('/add')
@login_required
def addtransaction():
    return redirect('.index')
