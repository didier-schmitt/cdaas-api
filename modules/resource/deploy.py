#!/usr/bin/env python

from helper.jenkins import JenkinsHelper
from flask_restful import Resource, reqparse, abort
from flask_security import current_user

job_deploy = 'mid/job/parameterized'

class Deploy(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('who', required=True, help='A person')
        parser.add_argument('greeting', default='Hello', help='A greeting', dest='greet')
        args = parser.parse_args()
        
        if args['greet'] not in ['Hello', 'Hi'] and not current_user.has_role('admin'):
            abort(400, message='The greeting shall be either Hello or Hi or shall not be.')
        
        return JenkinsHelper(job_deploy).build(args)

class DeployStatus(Resource):
    def get(self, status_id):
        return JenkinsHelper(job_deploy).status(status_id)

class DeployListStatus(Resource):
    def get(self):
        return JenkinsHelper(job_deploy).builds()

class DeployOutput(Resource):
    def get(self, status_id):
        return JenkinsHelper(job_deploy).output(status_id)