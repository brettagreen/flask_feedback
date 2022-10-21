from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship("Feedback", backref="users", cascade="all, delete")

    @classmethod
    def get_user(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_pw_hash(cls, password):
        hashed = bcrypt.generate_password_hash(password)
        hashed = hashed.decode("utf8")
        return hashed
    
    @classmethod
    def check_pw(cls, username, password):
        user = cls.get_user(username)
        if user:
            success = bcrypt.check_password_hash(user.password, password)
            return success
        else:
            return False

class Feedback(db.Model):
    """Feedback model"""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String, nullable=False)
    username = db.Column(db.String, db.ForeignKey('users.username'))

class Token(db.Model):
    """PasswordToken model"""
    __tablename__ = 'tokens'

    token = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('users.username'))

