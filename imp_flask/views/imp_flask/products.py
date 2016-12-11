from flask import render_template

from imp_flask.blueprints import products
from imp_flask.models.imps import Product


@products.route('/', defaults=dict(page=1))
@products.route('/page/<int:page>')
def index(page):
    if page == 0:
        page = 1
    pagination = Product.query.order_by('name').paginate(page, per_page=25, error_out=False)
    return render_template('products.html', pagination=pagination)
