import os
from setuptools import setup, Command

class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name = "cdaas-api",
    version = "1.0.0",
    packages = [
        "security",
        "admin",
        "config",
        "dao",
        "helpers"
    ],
    install_requires=[
        "Flask",
        "Flask-RESTful",
        "Flask-SQLAlchemy",
        "Flask-Security",
        "Flask-HTTPAuth",
        "Flask-Script",
        "Jinja2"
    ],
    zip_safe = False,
    cmdclass = {
        "clean": CleanCommand
    }
)
