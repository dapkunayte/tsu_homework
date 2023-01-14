from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    homeworks = db.relationship('HomeworkModel', backref='users', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)


class HomeworkModel(db.Model):
    __tablename__ = 'homeworks'

    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=False)  # date
    subject = db.Column(db.String(100), nullable=False, unique=False)
    task = db.Column(db.String(200), nullable=False, unique=False)  # задание
    username = db.Column(db.String(50), db.ForeignKey('users.username'))

    def __init__(self, date, subject, task, username):
        self.date = date
        self.subject = subject
        self.task = task
        self.username = username

    def __repr__(self):
        return f"<Homework {self.subject}>"
