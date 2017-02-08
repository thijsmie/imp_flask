from flask import render_template, request, url_for, redirect
from flask.json import jsonify
from flask_login import login_required

from imp_flask.blueprints import products
from imp_flask.models.imps import Product, Mod
from imp_flask.extensions import db, validate
from imp_flask.core import flash
from imp_flask.core.auth import ensure_user_admin


@products.route('/', defaults=dict(page=1))
@products.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1

    showhidden = request.args.get('showhidden','') == "True";
    
    pagination = Product.query.filter_by(hidden=showhidden).order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_products.html', showgroup=True, pagination=pagination, showhidden=showhidden)


@products.route('/group/<group>', defaults=dict(page=1))
@products.route('/group/<group>/page/<int:page>')
@login_required
def showgroup(group, page):
    if page <= 0:
        page = 1

    pagination = Product.query.filter(Product.group == group).order_by('id').paginate(page, per_page=20, error_out=False)
    return render_template('imp_flask_products.html', showgroup=False, pagination=pagination)


@products.route('/add', defaults=dict(product_id=0), methods=["GET", "POST"]) 
@products.route('/edit/<int:product_id>', methods=["GET", "POST"])
@login_required
@ensure_user_admin
def product(product_id):
    form = request.json
    
    if (product_id == 0):
        product = Product()
        to_add = True
    else:
        product = Product.query.get_or_404(product_id)
        to_add = False
    
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
            product.amount = form.get('amount', 0 if to_add else product.amount)
            product.value = form.get('value', 0 if to_add else product.value)
            product.allow_negative = form.get('allow_negative', False if to_add else product.allow_negative)
            product.value_constant = form.get('value_constant', False if to_add else product.value_constant)
            product.hidden = form.get('hidden', False if to_add else product.hidden)
            product.losemods = [Mod.query.get(id) for id in (form['losemods'] or ([] if to_add else product.losemods))]
            product.gainmods = [Mod.query.get(id) for id in (form['gainmods'] or ([] if to_add else product.gainmods))]
            
            if to_add:
                db.session.add(product)
            db.session.commit()
            
            return jsonify({})
    if to_add:
        return render_template('imp_flask_product.html', mods=Mod.query.all())
    else:
        return render_template('imp_flask_product.html', product=product, mods=Mod.query.all())
    
