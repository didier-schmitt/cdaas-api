#!/usr/bin/env python

from flask_restful import Api

from app import app
from security.auth import user_bp
from resource.socle import Socle, SocleStatus, SocleListStatus, SocleOutput
from resource.deploy import Deploy, DeployStatus, DeployListStatus, DeployOutput

user_api = Api(user_bp)

user_api.add_resource(Socle, '/socle/install')
user_api.add_resource(SocleListStatus, '/socle/install/')
user_api.add_resource(SocleStatus, '/socle/install/<status_id>')
user_api.add_resource(SocleOutput, '/socle/install/<status_id>/output')

user_api.add_resource(Deploy, '/app/deploy')
user_api.add_resource(DeployListStatus, '/app/deploy/')
user_api.add_resource(DeployStatus, '/app/deploy/<status_id>')
user_api.add_resource(DeployOutput, '/app/deploy/<status_id>/output')

app.register_blueprint(user_bp)
