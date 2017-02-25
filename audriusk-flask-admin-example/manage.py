from flask.ext.script import Manager

from flask_admin_example import app
from flask_admin_example.model import init_db, clear_db

manager = Manager(app)


@manager.command
def initdb():
    """Initialize database."""
    with app.app_context():
        init_db()


@manager.command
def cleardb():
    """Clear database."""
    with app.app_context():
        clear_db()


if __name__ == '__main__':
    manager.run()
