# coding: utf-8
import time

from bottle import request
from bottle import DEBUG
from bottle import TEMPLATE_PATH, Jinja2Template


MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY
YEAR = 12 * MONTH


def datetimeformat(value):
    """filter for Jinja2"""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def time_passed(value):
    """filter for Jinjia2"""
    time_diff = int(time.time() - time.mktime(value.timetuple()))
    if time_diff < MINUTE:
        quantity = time_diff
        unit = u'秒'
    if time_diff >= MINUTE and time_diff < HOUR:
        quantity = time_diff / MINUTE
        unit = u'分钟'
    if time_diff >= HOUR and time_diff < DAY:
        quantity = time_diff / HOUR
        unit = u'小时'
    if time_diff >= DAY and time_diff < MONTH:
        quantity = time_diff / DAY
        unit = u'天'
    if time_diff >= MONTH and time_diff < YEAR:
        quantity = time_diff / MONTH
        unit = u'月'
    if time_diff >= YEAR:
        quantity = time_diff / YEAR
        unit = u'年'

    return u'%s %s前' % (quantity, unit)


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
            'filters': {'datetimeformat': datetimeformat,
                        'time_passed': time_passed}
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
