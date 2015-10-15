# coding: utf-8
import bottle
import os.path

from bottle_login import LoginPlugin
from daimaduan.jinja_ext import JinajaPlugin

app_root = os.path.dirname(__file__)
app = bottle.default_app()

# Auto cast `site.debug` to boolean type.
config_file = os.path.join(app_root, 'config.cfg')
app.config.meta_set('site.debug', 'filter', bool)
app.config.load_config(config_file)
app.config['SECRET_KEY'] = app.config['site.secret_key']

# Setup bottle debug mode through config `site.debug`
bottle.debug(app.config['site.debug'])

jinja = JinajaPlugin(template_path=os.path.join(app_root, 'templates'))
login = LoginPlugin()

app.install(login)
app.install(jinja)
