# coding: utf-8
import bottle

from bottle_login import LoginPlugin
from daimaduan.jinja_ext import JinajaPlugin

app = bottle.default_app()

# Auto cast `site.debug` to boolean type.
app.config.meta_set('site.debug', 'filter', bool)
app.config.load_config('config.cfg')
app.config['SECRET_KEY'] = app.config['site.secret_key']

# Setup bottle debug mode through config `site.debug`
bottle.debug(app.config['site.debug'])

jinja = app.install(JinajaPlugin())
login = app.install(LoginPlugin())