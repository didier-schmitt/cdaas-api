#!/usr/bin/env python

from app import app
import endpoints

if __name__ == "__main__":
    app.run(host=app.config['LISTEN_ADDRESS'])