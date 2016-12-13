from flask import render_template, redirect, url_for, request, abort
from urllib.parse import urlparse, urljoin

from imp_flask.blueprints import home_index
from imp_flask.forms.login import Login
from imp_flask.core.auth import do_login, do_logout
from imp_flask.core import flash


# See http://flask.pocoo.org/snippets/62/ and https://flask-login.readthedocs.io/en/latest/#login-example
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@home_index.route('/')
def index():
    return render_template('home_index.html')


@home_index.route('/login', methods=["GET", "POST"])
def login():
    form = Login()
    if form.validate_on_submit():
        next_page = request.args.get('next')
        if next_page is not None:
            if not is_safe_url(next_page):
                flash.danger("A open redirect was attempted and prevented, did someone mess with your login link?")
                return abort(400)

        if do_login(form.username.data, form.password.data):
            flash.success("Logged in successfully.")
            return redirect(next_page or url_for('.index'))
        else:
            flash.danger("Incorrect login data, please try again")
    return render_template('home_login.html', form=form)


@home_index.route('/logout')
def logout():
    do_logout()
    return redirect(url_for('.index'))
