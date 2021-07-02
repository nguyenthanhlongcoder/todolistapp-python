from sqlalchemy.orm import relationship

from main import db
from sqlalchemy import Sequence, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    user_id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = relationship('Task', back_populates='user')
    def __repr__(self):
        return '<User full name: {} {}, email: {}>'.format(self.first_name, self.last_name, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    task_id = db.Column(db.Integer, Sequence('task_id_seq'), primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.user_id'))
    user = relationship('User', back_populates='tasks')
    priority_id = db.Column(db.Integer, ForeignKey('priority.priority_id'))
    priority = relationship('Priority', back_populates='tasks')
    status = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return '<Task: {} of user {}>'.format(self.description, self.user_id)
    def getClassPriority(self):
        if self.priority.description == '1st':
            return 'table-primary'
        elif self.priority.description == '2nd':
            return 'table-secondary'
        elif self.priority.description == '3rd':
            return 'table-success'
        else:
            return 'table-danger'

class Priority(db.Model):
    priority_id = db.Column(db.Integer, Sequence('priority_id_seq'), primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    tasks = relationship('Task', back_populates='priority')

    def __repr__(self):
        return '<Priority: {} of user {}>'.format(self.description)

db.create_all()


