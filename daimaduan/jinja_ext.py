from bottle import request
from bottle import DEBUG
from bottle import TEMPLATE_PATH, Jinja2Template

def view_name():
    try:
        return request.route.name.split('.')[0]
    except:
        return 'errors'

def view_func():
    try:
        return request.route.name.split('.')[-1]
    except:
        return 'error'

class JinajaPlugin(object):
    name = 'jinja_ext'
    api  = 2

    def setup(self, app):
        self.app = app

        TEMPLATE_PATH[:] = ['templates']

        Jinja2Template.settings = {
            'autoescape': True,
        }

        Jinja2Template.defaults = {
            'request': request,
            'view_name': view_name,
            'view_func': view_func,
            'config': app.config,
            'debug': DEBUG
        }

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper


