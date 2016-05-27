# coding: utf-8

import logging
from werkzeug.local import LocalProxy

def init_app(app):    
    if app.config['DEBUG']:
        app.logger.handlers[0].setFormatter(logging.Formatter(
            '[%(asctime)s %(levelname)7s] %(message)s '
            '(in %(filename)s:%(lineno)d)'))
    else:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s %(levelname)7s] %(message)s'))
        app.logger.addHandler(handler)

def get_logger():
    from flask import current_app
    return LocalProxy(lambda: current_app.logger)