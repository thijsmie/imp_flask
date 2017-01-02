from flask import render_template, request, url_for, redirect
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
            messages = []
            for error in errors:
                messages.append('.'.join(list(error.path)) + ": " + error.message)
            response = jsonify(messages=messages)
            response.status_code = 400
            return response
        else:
            product = Product()
            product.name = form['name']
            product.group = form['group']
            product.amount = form.get('amount', 0)
            product.value = form.get('value', 0)
            product.allow_negative = form.get('allow_negative', False)
            product.value_constant = form.get('value_constant', False)
            product.hidden = False
            product.losemods = [Mod.query.get(id) for id in (form['losemods'] or [])]
            product.gainmods = [Mod.query.get(id) for id in (form['gainmods'] or [])]
            
            db.session.add(product)
            db.session.commit()
            return jsonify({})
            
    return render_template('imp_flask_newproduct.html', mods=Mod.query.all())
    
    
@products.route('/edit/<int:product_id>', methods=["GET", "POST"])
@login_required
def editproduct():
    form = request.json
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == "POST":
        errors = validate(form, 'product', get_errors=True)
        if type(errors) == list:
            messages = []
            for error in errors:
                messages.append('.'.join(list(error.path)) + ": " + error.message)
            response = jsonify(messages=messages)
            response.status_code = 400
            return response
        else:
            product.name = form['name']
            product.group = form['group']
            product.amount = form.get('amount', 0)
            product.value = form.get('value', 0)
            product.allow_negative = form.get('allow_negative', False)
            product.value_constant = form.get('value_constant', False)
            product.hidden = False
            product.losemods = [Mod.query.get(id) for id in (form['losemods'] or [])]
            product.gainmods = [Mod.query.get(id) for id in (form['gainmods'] or [])]
            
            db.session.add(product)
            db.session.commit()
            return jsonify({})
            
    return render_template('imp_flask_newproduct.html', product=product mods=Mod.query.all())
    
