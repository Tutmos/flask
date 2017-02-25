from flask import abort, current_app
from flask.ext.admin import AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.login import current_user
from wtforms.fields import TextField, PasswordField
from wtforms.validators import Optional

from .model import User


class AuthMixin(object):
    def _handle_view(self, name, **kwargs):
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        if not current_user.admin:
            abort(403)


# Needed to protect index page of admin panel.
class IndexView(AuthMixin, AdminIndexView):
    pass


class UserView(AuthMixin, ModelView):
    column_exclude_list = ('_password',)
    column_searchable_list = ('username', 'last_login_ip', 'current_login_ip')
    column_sortable_list = ('username', 'last_login_at', 'last_login_ip',
                            'current_login_at', 'current_login_ip')
    column_filters = ('active', 'admin')

    form_columns = ('username', 'password', 'active', 'admin')
    form_overrides = {
        'username': TextField,
        '_password': PasswordField,
    }
    form_args = {'password': {'validators': [Optional()]}}

    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(User, session, **kwargs)

    def update_model(self, form, model):
        # Do not set password if its field is empty.
        if not form._fields['password'].data:
            del form._fields['password']
        return super(UserView, self).update_model(form, model)
