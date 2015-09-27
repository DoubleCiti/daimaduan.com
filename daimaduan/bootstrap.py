# coding: utf-8
import bottle
from bottle import request
from bottle import TEMPLATE_PATH, Jinja2Template

from bottle_login import LoginPlugin


TEMPLATE_PATH[:] = ['templates']
Jinja2Template.settings = {
    'autoescape': True,
}
Jinja2Template.defaults = {
    'request': request
}


app = bottle.default_app()
app.config.load_config('config.cfg')
app.config['SECRET_KEY'] = app.config['site.secret_key']
login = app.install(LoginPlugin())
