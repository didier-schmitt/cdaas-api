#!/usr/bin/env python

import os
import logging
import logging.config
from flask import Flask

app = Flask(__name__)

app.config.from_object(os.environ['CDAAS_API_CONFIG'])

log_config = app.config['LOGGING_CONFIG']

if not os.path.isabs(log_config):
    curpath = os.path.dirname(os.path.realpath(__file__))
    relpath = os.path.join(curpath, log_config)
    log_config = os.path.realpath(relpath)

if os.path.exists(log_config):
    logging.config.fileConfig(log_config)
else:
    logging.basicConfig(level=logging.DEBUG)
