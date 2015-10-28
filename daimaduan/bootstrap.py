# coding: utf-8
import bottle
import logging

from bottle_login import LoginPlugin
from daimaduan.jinja_ext import JinajaPlugin
from rauth import OAuth2Service

app = bottle.default_app()

# Setup logger
logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('daimaduan')

# Auto cast `site.debug` to boolean type.
app.config.load_config('config.cfg')
app.config['SECRET_KEY'] = app.config['site.secret_key']

jinja = JinajaPlugin(template_path='templates')
login = LoginPlugin()

app.install(login)
app.install(jinja)

oauth_google = OAuth2Service(
    name=app.config['oauth.google.name'],
    client_id=app.config['oauth.google.client_id'],
    client_secret=app.config['oauth.google.client_secret'],
    authorize_url=app.config['oauth.google.authorize_url'],
    access_token_url=app.config['oauth.google.access_token_url'],
    base_url=app.config['oauth.google.base_url'])
