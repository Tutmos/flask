from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import UserMixin

from .hash_passwords import check_hash, make_hash


db_engine = None
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def init_engine(db_uri):
    global db_engine
    db_engine = create_engine(db_uri)
    db_session.configure(bind=db_engine)


def init_db():
    Base.metadata.create_all(bind=db_engine)
    u1 = User(username=u'foo', password=u'foo', admin=True)
    u2 = User(username=u'bar', password=u'bar')
    u3 = User(username=u'baz', password=u'baz', active=False)
    db_session.add_all([u1, u2, u3])
    db_session.commit()


def clear_db():
    Base.metadata.drop_all(bind=db_engine)


Base = declarative_base()
Base.query = db_session.query_property()


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False, unique=True)
    _password = Column('password', Text, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    admin = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime)
    last_login_ip = Column(Text)
    current_login_at = Column(DateTime)
    current_login_ip = Column(Text)

    def _set_password(self, password):
        self._password = make_hash(password)

    def _get_password(self):
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))

    def valid_password(self, password):
        """Check if provided password is valid."""
        return check_hash(password, self.password)

    def is_active(self):
        return self.active

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.id,
                                 self.username)
