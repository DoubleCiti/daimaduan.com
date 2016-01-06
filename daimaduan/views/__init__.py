from bottle import request
from bottle import jinja2_view
from bottle import Jinja2Template

from daimaduan import app
from daimaduan.bootstrap import login
from daimaduan.models import Code
from daimaduan.models import User
from daimaduan.models import Paste

import daimaduan.views.errors
import daimaduan.views.pastes
import daimaduan.views.users


@login.load_user
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.hook('before_request')
def before_request():
    request.user = login.get_user()


@app.hook('after_request')
def after_request():
    Jinja2Template.defaults['session'] = request.environ.get('beaker.session')


@app.get('/status')
def status():
    return {'pastes_count': Paste.objects().count(),
            'codes_count': Code.objects().count(),
            'users_count': User.objects().count()}
