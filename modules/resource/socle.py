#!/usr/bin/env python

from helper.rundeck import RundeckHelper
from flask_restful import Resource, reqparse

job_socle = '802d4ab5-f46f-47d7-abe2-79cd2bf2e965'

class Socle(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('who', required=True)
        parser.add_argument('greeting', default='Hello', help='Hi or Hello', dest='greet')
        args = parser.parse_args()
        
        return RundeckHelper(job_socle).run(args)

class SocleStatus(Resource):
    def get(self, status_id):
        return RundeckHelper(job_socle).status(status_id)
