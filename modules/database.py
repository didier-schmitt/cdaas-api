#!/usr/bin/env python

from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)
