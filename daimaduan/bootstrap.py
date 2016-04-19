# coding: utf-8
import os

import memcache
from celery import Celery
from flask import Flask
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask.ext.log import Logging
from flask.ext.cdn import CDN
from jinja2 import MemcachedBytecodeCache

from daimaduan.extensions import assets
from daimaduan.utils.filters import datetimeformat
from daimaduan.utils.filters import md
from daimaduan.utils.filters import ternary
from daimaduan.utils.filters import time_passed
from daimaduan.utils.filters import time_used


# set default CONFIG to config.cfg
if not os.environ.get('CONFIG', None):
    os.environ['CONFIG'] = 'custom_settings.py'


db = MongoEngine()
login_manager = LoginManager()
flask_log = Logging()
cdn = CDN()

app = Flask(__name__)
app.config.from_object('daimaduan.default_settings')
app.config.from_envvar('CONFIG')

db.init_app(app)
flask_log.init_app(app)
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
app.jinja_env.filters['time_used'] = time_used
app.jinja_env.filters['ternary'] = ternary
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['markdown'] = md
if app.config['USE_JINJA_CACHE']:
    app.jinja_env.bytecode_cache = MemcachedBytecodeCache(memcache.Client([app.config['MEMCACHED_URL']]))

login_manager.init_app(app)
assets.init_app(app)
cdn.init_app(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=True,
                    base_url='https://cn.gravatar.com/')
