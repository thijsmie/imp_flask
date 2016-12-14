from flask import render_template
from flask_login import login_required

from imp_flask.blueprints import products
from imp_flask.models.imps import Product


@products.route('/', defaults=dict(page=1))
@products.route('/page/<int:page>')
@login_required
def index(page):
    if page <= 0:
        page = 1
    pagination = Product.query.order_by('id').paginate(page, per_page=25, error_out=False)
    return render_template('imp_flask_products.html', pagination=pagination)
