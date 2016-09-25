#!/usr/bin/env python

from requests import request, ConnectionError, Timeout, HTTPError, RequestException
from flask_restful import abort
from flask import current_app

def raise_http_error(code, message, cause=None):
    data = { 'message': message }
    if cause is not None and isinstance(cause, Exception) and current_app.config['DEBUG']:
        data['cause'] = str(cause)
    abort(code, **data)

def http_request(method, url, **kwargs):
    try:
        response = request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except ConnectionError as e:
        raise_http_error(503, 'The server is temporarily unable to service your request due to '
            'maintenance downtime or capacity problems.  Please try again later', e)
    except Timeout as e:
        raise_http_error(504, 'The connection to an upstream server timed out', e)
    except HTTPError as e:
        raise_http_error(e.response.status_code, 'The proxy server received an invalid response '
            'from an upstream server', e)
    except (RequestException) as e:
        raise_http_error(500, 'The server encountered an internal error and was unable to complete your request. '
            'Either the server is overloaded or there is an error in the application', e)
