# coding: utf-8
import bottle
import logging
import mongoengine

from bottle_login import LoginPlugin
from daimaduan.jinja_ext import JinajaPlugin
from daimaduan.utils import oauth_config
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

mongoengine.connect(app.config['mongodb.database'], host=app.config['mongodb.host'])

app.install(login)
app.install(jinja)

oauth_services = {}
oauth_services['google'] = OAuth2Service(**oauth_config(app.config, 'google'))
oauth_services['github'] = OAuth2Service(**oauth_config(app.config, 'github'))
