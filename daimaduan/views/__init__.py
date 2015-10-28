from bottle import request
from bottle import Jinja2Template

from daimaduan.bootstrap import app
from daimaduan.bootstrap import login
from daimaduan.models import User

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
