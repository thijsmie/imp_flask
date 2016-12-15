from flask import render_template
from flask_login import login_required

from imp_flask.blueprints import products
from imp_flask.models.imps import Product, Mod
from imp_flask.forms.product import Product as ProductForm


@products.route('/', defaults=dict(page=1))
@products.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1

    pagination = Product.query.order_by('id').paginate(page, per_page=25, error_out=False)
    return render_template('imp_flask_products.html', showgroup=True, pagination=pagination)


@products.route('/group/<group>', defaults=dict(page=1))
@products.route('/group/<group>/page/<int:page>')
@login_required
def showgroup(group, page):
    if page <= 0:
        page = 1

    pagination = Product.query.filter(Product.group == group).order_by('id').paginate(page, per_page=25, error_out=False)
    return render_template('imp_flask_products.html', showgroup=False, pagination=pagination)


@products.route('/add')
@login_required
def addproduct():
    form = ProductForm()
    modlist = [(mod.id, mod.name) for mod in Mod.query.all()]
    form.gainmods.choices = modlist
    form.losemods.choices = modlist

    if form.validate_on_submit():
        return 'sumtin'
    return render_template('imp_flask_newproduct.html', form=form)