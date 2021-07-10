from sqlalchemy.orm import relationship
from datetime import datetime
from main import db
from sqlalchemy import Sequence, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    user_id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    project = relationship('Project', back_populates='user')
    def __repr__(self):
        return '<User full name: {} {}, email: {}>'.format(self.first_name, self.last_name, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    task_id = db.Column(db.Integer, Sequence('task_id_seq'), primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    priority_id = db.Column(db.Integer, ForeignKey('priority.priority_id'))
    priority = relationship('Priority', back_populates='tasks')
    status_id = db.Column(db.Integer, ForeignKey('status.status_id'))
    status = relationship('Status', back_populates='tasks')
    project_id = db.Column(db.Integer, ForeignKey('project.project_id'))
    project = relationship('Project', back_populates='tasks')
    def __repr__(self):
        return '<Task: {}>'.format(self.description)
    def getClassPriority(self):
        if self.priority.description == '1st':
            return 'table-primary'
        elif self.priority.description == '2nd':
            return 'table-secondary'
        elif self.priority.description == '3rd':
            return 'table-success'
        else:
            return 'table-danger'
    def getClassStatus(self):
        if self.status_id == 1:
            return 'btn btn-secondary'
        elif self.status_id == 2:
            return 'btn btn-primary'
        elif self.status_id == 3:
            return 'btn btn-danger'
        else:
            return 'btn btn-success'

class Priority(db.Model):
    priority_id = db.Column(db.Integer, Sequence('priority_id_seq'), primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    tasks = relationship('Task', back_populates='priority')

    def __repr__(self):
        return '<Priority: {} of user {}>'.format(self.description)

class Project(db.Model):
    __searchable__ = ['name']
    project_id = db.Column(db.Integer, Sequence('project_id_seq'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.String(255), nullable=True)
    deadline = db.Column(db.DateTime ,nullable=False, default=datetime.utcnow())

    user_id = db.Column(db.Integer, ForeignKey('user.user_id'))
    user = db.relationship('User', back_populates = 'project')

    status_id = db.Column(db.Integer, ForeignKey('status.status_id'))
    status = db.relationship('Status', back_populates = 'project')

    tasks = db.relationship('Task', back_populates = 'project')
    def getClassStatus(self):
        if self.status_id == 1:
            return 'btn btn-secondary'
        elif self.status_id == 2:
            return 'btn btn-primary'
        elif self.status_id == 3:
            return 'btn btn-danger'
        else:
            return 'btn btn-success'

    def __repr__(self):
        return '<Project: {} of user {} projectname {} deadline {}>'.format(self.project_id, self.user_id, self.name, self.deadline)

class Status(db.Model):
    status_id = db.Column(db.Integer, Sequence('status_id_seq'), primary_key = True)
    desc = db.Column(db.String(255), nullable = False)
    tasks = db.relationship('Task', back_populates = 'status')
    project = db.relationship('Project', back_populates = 'status')

    def __repr__(self):
            return '<Status: {} desc {} >'.format(self.status_id, self.desc)

db.create_all()


