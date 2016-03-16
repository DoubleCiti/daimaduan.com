# coding: utf-8
import os

from celery import Celery
from flask import Flask
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_mongoengine import MongoEngine

from daimaduan.extensions import assets
from daimaduan.utils.filters import datetimeformat
from daimaduan.utils.filters import md
from daimaduan.utils.filters import ternary
from daimaduan.utils.filters import time_passed


# set default CONFIG to config.cfg
if not os.environ.get('CONFIG', None):
    os.environ['CONFIG'] = 'config.cfg'


db = MongoEngine()
login_manager = LoginManager()

app = Flask(__name__)
app.config.from_object('daimaduan.default_settings')
app.config.from_envvar('CONFIG')
db.init_app(app)
celery = Celery(__name__)
celery.conf.add_defaults(app.config)

from daimaduan.views.sites import site_app
from daimaduan.views.users import user_app
from daimaduan.views.pastes import paste_app
from daimaduan.views.tags import tag_app
from daimaduan.views.bookmarks import bookmark_app

app.register_blueprint(site_app)
app.register_blueprint(user_app, url_prefix='/user')
app.register_blueprint(paste_app, url_prefix='/paste')
app.register_blueprint(tag_app, url_prefix='/tag')
app.register_blueprint(bookmark_app, url_prefix='/bookmark')

app.jinja_env.filters['time_passed'] = time_passed
app.jinja_env.filters['ternary'] = ternary
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['markdown'] = md

login_manager.init_app(app)
assets.init_app(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=True,
                    base_url=None)

# app.config.load_config('%s/config.cfg' % get_current_path())
# # Check if there's a key in env variables
# # if you want to set config on the fly, use env var
# # a.b.c in config => A_B_C in env var
# for key in app.config.keys():
#     k = key.replace('.', '_').upper()
#     if k in os.environ:
#         app.config[key] = os.environ[k]
# app.config['SECRET_KEY'] = app.config['site.validate_key']
#
# oauth_services = {}
# oauth_services['google'] = OAuth2Service(**oauth_config(app.config, 'google'))
# oauth_services['github'] = OAuth2Service(**oauth_config(app.config, 'github'))
