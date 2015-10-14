from bottle import request
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

TEMPLATE_PATH[:] = ['templates']

Jinja2Template.settings = {
    'autoescape': True,
}

Jinja2Template.defaults = {
    'request': request,
    'view_name': view_name,
    'func_name': func_name
}

