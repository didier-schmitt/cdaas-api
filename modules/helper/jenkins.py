#!/usr/bin/env python

import requests
from datetime import datetime
from app import app
from flask_restful import abort, marshal
import helper.status
from flask_security import current_user

queue_id_prefix = '-'
queue_id_expiration = 180

action_tree     = 'actions[parameters[name,value],causes[userId]]'
build_tree      = 'id,timestamp,building,result,%s' % action_tree
queue_tree      = 'id,inQueueSince,cancelled,executable[%s],%s' % (build_tree, action_tree)
build_list_tree = 'builds[%s]' % build_tree

class JenkinsHelper:
    """
    Helpers functions for building jobs and retrieving jobs executions
    """
    jenkins_url = app.config['JENKINS_URL']
    ca_bundle = app.config['CA_BUNDLE']
    token = None
    job = None

    def __init__(self, job):
        self.job = job
        self.token = current_user.jenkins_key

    def build(self, data=None):
        """
        Build a job
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic %s' % self.token
        }
        if data is None:
            endpoint = '%s/job/%s/build' % (self.jenkins_url, self.job)
            response = requests.post(endpoint, headers=headers, verify=self.ca_bundle)
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            endpoint = '%s/job/%s/buildWithParameters' % (self.jenkins_url, self.job)
            response = requests.post(endpoint, headers=headers, data=data, verify=self.ca_bundle)

        if response.status_code == 201:
            # Job launched in Build Queue
            params = {
                'tree': queue_tree
            }
            endpoint = '%sapi/json' % response.headers['Location']
            response = requests.get(endpoint, params=params, headers=headers, verify=self.ca_bundle)
            if response.status_code == 200:
                headers = {}
                model = self.queue_to_model(response.json())
                if 'id-expires' in model:
                    headers['Cache-Control'] = 'max-age=%d' % model['id-expires']
                return marshal(model, helper.status.status_model), 200, headers
            else:
                abort(500)
        else:
            # Something has gone wrong...
            abort(500)

    def status(self, status_id):
        """
        Retrieves the status for a job build (either it is in the queue or running on a slave)
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic %s' % self.token
        }
        parsed_id, is_queued = self.parse_status(status_id)
        if is_queued:
            params = {
                'tree': queue_tree
            }
            endpoint = '%s/queue/item/%s/api/json' % (self.jenkins_url, parsed_id)
            response = requests.get(endpoint, params=params, headers=headers, verify=self.ca_bundle)
            if response.status_code == 404:
                abort(404)
            elif response.status_code == 200:
                headers = {}
                model = self.queue_to_model(response.json())
                if 'id-expires' in model:
                    headers['Cache-Control'] = 'max-age=%d' % model['id-expires']
                return marshal(model, helper.status.status_model), 200, headers
            else:
                abort(500)
        else:
            params = {
                'tree': build_tree
            }
            endpoint = '%s/job/%s/%s/api/json' % (self.jenkins_url, self.job, parsed_id)
            response = requests.get(endpoint, params=params, headers=headers, verify=self.ca_bundle)
            if response.status_code == 404:
                abort(404)
            elif response.status_code == 200:
                return marshal(self.build_to_model(response.json()), helper.status.status_model)
            else:
                abort(500)

    def output(self, status_id):
        """
        Retrieves the Console Output for a job build
        """
        headers = {
            'Accept': 'text/plain',
            'Authorization': 'Basic %s' % self.token
        }
        endpoint = '%s/job/%s/%s/consoleText' % (self.jenkins_url, self.job, status_id)
        response = requests.get(endpoint, headers=headers, verify=self.ca_bundle)
        if response.status_code == 404:
            abort(404)
        elif response.status_code == 200:
            return response.text.splitlines()
        else:
            abort(500)

    def builds(self):
        """
        List all builds for a job
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Basic %s' % self.token
        }
        params = {
            'tree': build_list_tree
        }
        endpoint = '%s/job/%s/api/json' % (self.jenkins_url, self.job)
        response = requests.get(endpoint, params=params, headers=headers, verify=self.ca_bundle)
        if response.status_code == 404:
            abort(404)
        elif response.status_code == 200:
            j = response.json()
            return marshal([self.build_to_model(b) for b in j['builds']], helper.status.status_model)
        else:
            abort(500)

    def parse_status(self, status_id):
        """
        return the tuple (parsed_is, is_queued) from a status id
        """
        if status_id.startswith(queue_id_prefix):
            return status_id[1:], True
        else:
            return status_id, False

    def build_to_model(self, response_data):
        """
        wraps a jenkins build response into an api standard status response_data
        """
        if response_data['building'] == True:
            status = helper.status.STATUS_RUNNING
        if response_data['result'] ==  'SUCCESS' or response_data['result'] ==  'UNSTABLE':
            status = helper.status.STATUS_SUCCEEDED
        if response_data['result'] ==  'FAILURE':
            status = helper.status.STATUS_FAILED
        if response_data['result'] ==  'ABORTED':
            status = helper.status.STATUS_CANCELLED

        model = {
            'id':         response_data['id'],
            'status':     status,
            'started-at': datetime.fromtimestamp(response_data['timestamp']/1000)
        }
        if 'actions' in response_data:
            model.update(self.actions_to_model(response_data['actions']))

        return model

    def queue_to_model(self, response_data):
        """
        wraps a jenkins queue item response into an api standard status response_data
        """
        if 'executable' in response_data and not response_data['executable'] is None:
            return self.build_to_model(response_data['executable'])

        if 'cancelled' in response_data and response_data['cancelled'] == True:
            status = helper.status.STATUS_CANCELLED
        else:
            status = helper.status.STATUS_PENDING

        status_id = '%s%s' % (queue_id_prefix, response_data['id'])
        model = {
            'id':         status_id,
            'id-expires': queue_id_expiration,
            'status':     status,
            'started-at': datetime.fromtimestamp(response_data['inQueueSince']/1000)
        }
        if 'actions' in response_data:
            model.update(self.actions_to_model(response_data['actions']))

        return model

    def actions_to_model(self, actions):
        """
        wraps the actions returned by Jenkins into api standard data
        """
        model = {}
        if actions is None:
            return model
        
        for action in actions:
            if type(action) is dict:
                if 'parameters' in action:
                    p = {}
                    for parameter in action['parameters']:
                        p[parameter['name']] = parameter['value']
                    model['parameters'] = p
                if 'causes' in action:
                    for cause in action['causes']:
                        if 'userId' in cause:
                            model['started-by'] = cause['userId']
                            break
        return model