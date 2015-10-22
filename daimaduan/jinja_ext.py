"""
    daimaduan.jinja_ext
    -------------------

    A bottle plugin to setup and extend jinaja enviroment.

"""

from bottle import request
from bottle import DEBUG
from bottle import TEMPLATE_PATH, Jinja2Template


def view_name():
    """Get request's view name

    In the following example, the view name will be `pastes`

        @app.route('/', name='pastes.index')

    If faild to get the view name, `errors` will be returned instead.
    """

    try:
        return request.route.name.split('.')[0]
    except:
        return 'errors'


def view_func():
    """Get request's function name.

    In the following example, the function name will be `index`

        @app.route('/', name='pastes.index')

    If faild to get the function name, `error` will be returned instead.
    """

    try:
        return request.route.name.split('.')[-1]
    except:
        return 'error'


class JinajaPlugin(object):
    name = 'jinja_ext'
    api = 2

    def __init__(self, template_path='templates'):
        self.template_path = template_path

    def setup(self, app):
        self.app = app

        TEMPLATE_PATH[:] = [self.template_path]

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
