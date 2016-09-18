#!/usr/bin/env python

from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from app import app
from database import db

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    api_key = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(50))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    jenkins_key = db.Column(db.String(255))
    rundeck_key = db.Column(db.String(255))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def create_realm():
    db.create_all()

    b = user_datastore.create_user(api_key='bobby', name='Bobby', jenkins_key='YWRtaW46YWRtaW4=', rundeck_key='SOoRlwbgWx9xc8JCly9gkdgwALFYB0Xo')
    f = user_datastore.create_user(api_key='freddie', name='Freddie', jenkins_key='YnVpbGRlcjpidWlsZGVy')
    t = user_datastore.create_user(api_key='tommy', name='Tommy')

    a = user_datastore.create_role(name='admin')
    u = user_datastore.create_role(name='user')

    user_datastore.add_role_to_user(b, a)
    user_datastore.add_role_to_user(b, u)
    user_datastore.add_role_to_user(f, u)
    db.session.commit()
