#!/usr/bin/env python

from flask import request, _request_ctx_stack, Blueprint
from flask_security import current_user
from flask_principal import identity_changed, Identity
from security.models import User
from security.messages import Http_Response
from app import app

@app.before_request
def authenticate():
    token = request.headers.get('Authorization')
    if token:
        user = User.query.filter_by(api_key=token).first()
        if user:
            # Hijack Flask-Login to set current_user
            _request_ctx_stack.top.user = user
            identity_changed.send(app, identity=Identity(user.id))
        else:
            return Http_Response.UNAUTHORIZED
    else:
        return Http_Response.UNAUTHENTICATED

user_bp = Blueprint('user_bp', __name__)

def authorize(role):
    if not current_user.is_authenticated:
        return Http_Response.UNAUTHENTICATED
    if not current_user.has_role(role):
        return Http_Response.FORBIDDEN
    return None

@user_bp.before_request
def authorize_user():
    return authorize('user')
