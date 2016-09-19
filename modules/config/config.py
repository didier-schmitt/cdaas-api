#!/usr/bin/env python

class Config(object):
    DEBUG          = False
    SECRET_KEY     = 'forgetme'
    CA_BUNDLE      = '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem'
    LISTEN_ADDRESS = '0.0.0.0'

class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME = 'dev-cdaas.sws.group.gca:5010'
    LOGGING_CONFIG = '../conf/logging.cfg'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../data/db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JENKINS_URL = 'https://dev-cdaas.sws.group.gca/jenkins'
    RUNDECK_URL = 'https://dev-cdaas.sws.group.gca/rundeck'

class ProductionConfig(Config):
    DEBUG = False
    SERVER_NAME    = 'cdaas.sws.group.gca:5000'
    LOGGING_CONFIG = '../conf/logging.cfg'
    JENKINS_URL    = 'https://cdaas.sws.group.gca/jenkins'
    RUNDECK_URL    = 'https://cdaas.sws.group.gca/rundeck'

class LocalConfig(DevelopmentConfig):
    SERVER_NAME    = 'localhost:5020'
    JENKINS_URL    = 'http://cdaas.localdomain'
    RUNDECK_URL    = 'http://cdaas.localdomain:4440'
    LISTEN_ADDRESS = '127.0.0.1'