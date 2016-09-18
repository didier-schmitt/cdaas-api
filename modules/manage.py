#!/usr/bin/env python

from flask_script import Manager
from app import app
from database import db
from security.models import create_realm

manager = Manager(app)

@manager.option('-n', '--name', dest='name', default='joe')
def hello(name):
    print "hello%s" % name 

@manager.command
def create_db():
    create_realm()

if __name__ == "__main__":
    manager.run()
