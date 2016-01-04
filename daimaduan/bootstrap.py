# coding: utf-8
import logging
import os

import bottle
from bottle_login import LoginPlugin
from rauth import OAuth2Service

from daimaduan.extensions.jinja import JinajaPlugin
from daimaduan.extensions.mongo import MongoenginePlugin
from daimaduan.utils.oauth import oauth_config


def get_current_path():
    file_name = os.path.dirname(__file__)
    return os.path.abspath(file_name)


logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('daimaduan')


app = bottle.default_app()

app.config.load_config('%s/config.cfg' % get_current_path())
# Check if there's a key in env variables
# if you want to set config on the fly, use env var
# a.b.c in config => A_B_C in env var
for key in app.config.keys():
    k = key.replace('.', '_').upper()
    if k in os.environ:
        app.config[key] = os.environ[k]
app.config['SECRET_KEY'] = app.config['site.validate_key']

jinja = JinajaPlugin(template_path='%s/templates' % get_current_path())
login = LoginPlugin()

app.install(login)
app.install(jinja)
app.install(MongoenginePlugin())

oauth_services = {}
oauth_services['google'] = OAuth2Service(**oauth_config(app.config, 'google'))
oauth_services['github'] = OAuth2Service(**oauth_config(app.config, 'github'))
