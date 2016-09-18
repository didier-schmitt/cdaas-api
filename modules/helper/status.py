#!/usr/bin/env python

from flask_restful import fields

STATUS_PENDING   = 'pending'
STATUS_RUNNING   = 'running'
STATUS_CANCELLED = 'cancelled'
STATUS_FAILED    = 'failed'
STATUS_SUCCEEDED = 'succeeded'
STATUS_UNKNOWN   = 'unknown'

status_model = {
    'id':         fields.String,
    'status':     fields.String(default=STATUS_UNKNOWN),
    'started-at': fields.DateTime(dt_format='iso8601'),
    'started-by': fields.String(default='Unknown'),
    'parameters': fields.Raw 
}
