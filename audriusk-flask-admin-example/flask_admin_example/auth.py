from functools import wraps
from datetime import datetime

from flask import current_app, abort, request
from flask.ext.login import current_user, login_user as _login_user

from .model import db_session


def is_admin():
    """Check if current user is authenticated and authorized.

    Meant to be used inside views and templates to protect part of resources.
    """
    return current_user.is_authenticated() and current_user.admin


def admin_login_required(fn):
    """
    Ensure that current user is authenticated and authorized to access the
    decorated view.  For example::

        @app.route('/protected')
        @admin_login_required
        def protected():
            pass

    """
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        if not current_user.admin:
            abort(403)
        return fn(*args, **kwargs)
    return decorated_view


def login_user(user, **kwargs):
    """Log in user and save time and IP address on success."""
    result = _login_user(user, **kwargs)
    if result:
        user.last_login_at = user.current_login_at
        user.current_login_at = datetime.utcnow()
        user.last_login_ip = user.current_login_ip
        user.current_login_ip = request.remote_addr
        db_session.commit()
    return result
