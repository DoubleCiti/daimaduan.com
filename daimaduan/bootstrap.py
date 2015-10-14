# coding: utf-8
import bottle

import daimaduan.jinja_ext

from bottle_login import LoginPlugin

app = bottle.default_app()
app.config.load_config('config.cfg')
app.config['SECRET_KEY'] = app.config['site.secret_key']

login = app.install(LoginPlugin())