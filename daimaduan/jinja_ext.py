from bottle import request
from bottle import DEBUG
from bottle import TEMPLATE_PATH, Jinja2Template

def view():
    return request.route.callback

def view_name():
    try:
        return view().__module__.replace('daimaduan.views.', '')
    except:
        return 'unknown'

def func_name():
    try:
        return view().__name__
    except:
        return 'unknown'

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
            'func_name': func_name,
            'config': app.config,
            'debug': DEBUG
        }

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper


