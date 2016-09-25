#!/usr/bin/env python

from http_client import http_request, raise_http_error
from datetime import datetime
from flask import current_app
from flask_restful import abort, marshal
from flask_security import current_user
import helper.status
from werkzeug.exceptions import NotFound

class RundeckHelper:
    """
    Helpers functions for running jobs and retrieving jobs activities
    """
    rdeck_url = None
    ca_bundle = None
    token = None
    job = None

    def __init__(self, job):
        self.rdeck_url = current_app.config['RUNDECK_URL']
        self.ca_bundle = current_app.config['CA_BUNDLE']
        self.job = job
        self.token = current_user.rundeck_key

    def _rdeck_call(self, method, path, params=None):
        headers = {
            'Accept': 'application/json',
            'X-Rundeck-Auth-Token': self.token
        }
        endpoint = "%s/%s" % (self.rdeck_url, path)
        return http_request(method, endpoint, params=params, headers=headers, verify=self.ca_bundle)

    def run(self, params=None):
        """
        Run a job
        """        
        endpoint = "api/14/job/%s/run" % self.job
        query = {'format': 'json'}
        if params is not None:
            query['argString'] = ' '.join(['-' + str(k) + ' ' + str(v) for k, v in params.items()])
        response = self._rdeck_call("POST", endpoint, query)
        return marshal(self.response_to_model(response.json()), helper.status.status_model)


    def status(self, exec_id):
        """
        Retrieves the status for a job execution
        """
        try:
            query = {
                'format': 'json'
            }
            endpoint = "api/14/execution/%s" % exec_id
            response = self._rdeck_call("GET", endpoint, query)
            j = response.json()
            # Check that the Execution ID matches the appropriate Job
            if j['job']['id'] != self.job:
                abort(404)
            return marshal(self.response_to_model(j), helper.status.status_model)
        except NotFound as e:
            raise_http_error(404, 'The requested status id does not exist', e)
    
    def output(self, exec_id):
        """
        Retrieves the output for a job execution
        """
        try:
            # Check that the Execution ID matches the appropriate Job
            self.status(exec_id)
            
            endpoint = "api/14/execution/%s/output.text" % exec_id
            response = self._rdeck_call('GET', endpoint)
            return response.text.splitlines()
        except NotFound as e:
            raise_http_error(404, 'The requested status id does not exist', e)

    def executions(self):
        """
        List all execution for a job
        """
        endpoint = 'api/14/job/%s/executions' % self.job
        query = { 'format': 'json' }
        response = self._rdeck_call('GET', endpoint, query)
        j = response.json()
        return marshal([self.response_to_model(execution) for execution in j['executions']], helper.status.status_model)

    def response_to_model(self, response_data):
        """
        wraps a rundeck job execution response into an api standard status response_data
        """
        if response_data['status'] == 'running':
            status = helper.status.STATUS_RUNNING
        elif response_data['status'] == 'succeeded':
            status = helper.status.STATUS_SUCCEEDED
        elif response_data['status'] == 'failed':
            status = helper.status.STATUS_FAILED
        elif response_data['status'] == 'aborted':
            status = helper.status.STATUS_CANCELLED
        else:
            status = helper.status.STATUS_UNKNOWN

        model = {
            'id':         response_data['id'],
            'started-at': datetime.fromtimestamp(response_data['date-started']['unixtime']/1000),
            'started-by': response_data['user'],
            'status':     status,
            'parameters': response_data['job']['options']
        }
        return model
