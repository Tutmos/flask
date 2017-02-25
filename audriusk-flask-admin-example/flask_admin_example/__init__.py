from datetime import timedelta

from flask import Flask, render_template, redirect, url_for, flash, session, \
    request
from flask.ext.admin import Admin
from flask.ext.login import LoginManager, logout_user, current_user, \
    login_required

from .model import User, init_engine, db_session
from .forms import LoginForm
from .admin import IndexView, UserView
from .auth import is_admin, login_user

DB_URI = 'sqlite:///users.db'
DEBUG = True
SECRET_KEY = 'xyyzy'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

app = Flask(__name__)
app.config.from_object(__name__)
app.jinja_env.globals['is_admin'] = is_admin

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

admin = Admin(app, index_view=IndexView())
admin.add_view(UserView(db_session, name='Users', endpoint='users'))

init_engine(app.config['DB_URI'])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.teardown_request
def remove_db_session(exception=None):
    db_session.remove()


@app.errorhandler(403)
def forbidden_403(exception):
    return render_template('forbidden.jinja'), 403


@app.route('/')
def index():
    return render_template('index.jinja')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.valid_password(form.password.data):
            if login_user(user, remember=form.remember.data):
                # Enable session expiration only if user hasn't chosen to be
                # remembered.
                session.permanent = not form.remember.data
                flash('Logged in successfully!', 'success')
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash('This username is disabled!', 'error')
        else:
            flash('Wrong username or password!', 'error')
    return render_template('login.jinja', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out!')
    return redirect(url_for('index'))
