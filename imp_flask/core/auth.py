from flask_login import LoginManager, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import redirect
from imp_flask.core import flash
from functools import wraps

from imp_flask.models.auth import User
from imp_flask.extensions import LOG, db

# Random session key generation, inspired by django.utils.crypto.get_random_string
import random

try:
    random = random.SystemRandom()
except NotImplementedError:
    LOG.critical("Insecure random! Please make random.SystemRandom available!")


# noinspection PyUnusedLocal
def generate_session_key(length):
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(length)])


auth = LoginManager()
auth.login_view = "home.index.login"
auth.session_protection = "strong"

auth_hasher = Bcrypt()


@auth.user_loader
def load_user(session_token):
    return User.query.filter_by(token=session_token).first()


def do_login(username, password):
    user = User.query.filter_by(username=username).first()

    if user is None:
        return False

    if not auth_hasher.check_password_hash(user.passhash, password):
        return False

    user.token = generate_session_key(64)

    # DB session committing can introduce weird stuff if do_login is ever called in the middle of something.
    # So don't do that...
    db.session.commit()

    login_user(user)
    return True


def do_logout():
    logout_user()


def new_user(username, password, email, admin, relation=None, pos=None):
    user = User()
    user.username = username
    user.passhash = auth_hasher.generate_password_hash(password)
    user.email = email
    user.admin = admin

    if relation is not None:
        user.relation = relation

    if pos is not None:
        user.pos = pos

    return user


def ensure_user_admin(f):
    # Note, should be placed below @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            flash.danger("Your user account is not allowed to perform this action.")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def ensure_user_pos(f):
    # Note, should be placed below @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            if not (current_user.pos is not None and current_user.pos.id == kwargs['pos_id']):
                flash.danger("Your user account is not allowed to perform this action.")
                return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def ensure_user_relation(f):
    # Note, should be placed below @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            if not (current_user.relation is not None and current_user.relation.id == kwargs['relation_id']):
                flash.danger("Your user account is not allowed to perform this action.")
                return redirect('/')
        return f(*args, **kwargs)
    return decorated_function
