from flask import render_template, request
from flask.json import jsonify
from flask_login import login_required

from imp_flask.blueprints import products
from imp_flask.models.imps import Product, Mod
from imp_flask.extensions import db, validate
from imp_flask.core import flash


@products.route('/', defaults=dict(page=1))
@products.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1

    pagination = Product.query.order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_products.html', showgroup=True, pagination=pagination)


@products.route('/group/<group>', defaults=dict(page=1))
@products.route('/group/<group>/page/<int:page>')
@login_required
def showgroup(group, page):
    if page <= 0:
        page = 1

    pagination = Product.query.filter(Product.group == group).order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_products.html', showgroup=False, pagination=pagination)


@products.route('/add', methods=["GET", "POST"])
@login_required
def addproduct():
    form = request.json
    
    if request.method == "POST":
        errors = validate(form, 'newproduct', get_errors=True)
        if type(errors) == list:
            resp = jsonify(errors)
            resp.status_code = 400
            return resp
        else:
            product = Product()
            product.name = form['name']
            product.group = form['group']
            product.amount = form.get('amount', 0)
            product.value = form.get('value', 0)
            product.allow_negative = form.get('allow_negative', False)
            product.value_constant = form.get('value_constant', False)
            product.hidden = False
            product.losemods = form.get('losemods', [])
            product.gainmods = form.get('gainmods', [])
            
            db.session.add(product)
            db.session.commit()
            
    return render_template('imp_flask_newproduct.html', form=form, mods=Mod.query.all())

