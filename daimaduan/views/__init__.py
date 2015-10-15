from bottle import DEBUG
from bottle import request
from daimaduan.bootstrap import app
from daimaduan.bootstrap import login

from daimaduan.models import User

# Disable custom errors pages for debug.
if DEBUG:
    import daimaduan.views.errors

import daimaduan.views.pastes
import daimaduan.views.users

@login.load_user
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.hook('before_request')
def before_request():
    # this line is used for bottle-login plugin
    request.environ['session'] = request.environ.get('beaker.session')
    request.user = login.get_user()

@app.hook('after_request')
def after_request():
    # update beaker.session and then save it
    request.environ.get('beaker.session').update(request.environ['session'])
    request.environ.get('beaker.session').save()
