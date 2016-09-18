#!/usr/bin/env python

import json

class Http_Response():
    UNAUTHENTICATED = json.dumps(
                            {'message': 'You must authenticate to perform this request'}), \
                              401, \
                            {'Content-Type': 'application/json', 'WWW-Authenticate': 'Token realm="flask"'}

    UNAUTHORIZED = json.dumps(
                            {'message': 'You are not authorized to perform this request'}), \
                              401, \
                            {'Content-Type': 'application/json', 'WWW-Authenticate': 'Token realm="flask"'}

    FORBIDDEN = json.dumps(
                         {'message': 'You are not authorized to perform this request'}), \
                           403, \
                         {'Content-Type': 'application/json'}
