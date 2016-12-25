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
    form = request.form
    
    if request.method == "POST":
        errors = validate(form, 'newproduct', get_errors=True)
        if type(errors) == list:
            for error in errors:
                flash.warning('.'.join(list(error.path)) + ": " + error.message)
            return redirect(url_for('.addproduct'))
        else:
            product = Product()
            product.name = form['name']
            product.group = form['group']
            product.amount = int(form.get('amount', '0'))
            product.value = int(form.get('value', '0'))
            product.allow_negative = form.get('allow_negative', '') != ''
            product.value_constant = form.get('value_constant', '') != ''
            product.hidden = False
            
            if 'losemods' in form:
                product.losemods = [Mod.query.get_or_404(int(m_id)) for m_id in form.get('losemods', '').split(',')]
                
            if 'gainmods' in form:
                product.gainmods = [Mod.query.get_or_404(int(m_id)) for m_id in form.get('gainmods', '').split(',')]
            
            db.session.add(product)
            db.session.commit()
            
            flash.success("Product " + product.name + " was added to the database.")
            return redirect(url_for('.addproduct'))
            
    return render_template('imp_flask_newproduct.html', mods=Mod.query.all())
    
    
@products.route('/edit/<int:product_id>', methods=["GET", "POST"])
@login_required
def editproduct(product_id):
    form = request.form
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == "POST":
        errors = validate(form, 'newproduct', get_errors=True)
        if type(errors) == list:
            for error in errors:
                flash.warning('.'.join(list(error.path)) + ": " + error.message)
            return redirect(url_for('.editproduct', product_id=product_id))
        else:      
            product.name = form['name']
            product.group = form['group']
            product.amount = int(form.get('amount', '0'))
            product.value = int(form.get('value', '0'))
            product.allow_negative = form.get('allow_negative', '') != ''
            product.value_constant = form.get('value_constant', '') != ''
            product.hidden = False
            
            if 'losemods' in form:
                product.losemods = [Mod.query.get_or_404(int(m_id)) for m_id in form.get('losemods', '').split(',')]
            else:
                product.losemods = []
                
            if 'gainmods' in form:
                product.gainmods = [Mod.query.get_or_404(int(m_id)) for m_id in form.get('gainmods', '').split(',')]
            else:
                product.gainmods = []
            
            db.session.commit()
            
            flash.success("Product " + product.name + " was successfully edited.")
            return redirect(url_for('.editproduct', product_id=product_id))
            
    return render_template('imp_flask_editproduct.html', product=product, mods=Mod.query.all())    
    

