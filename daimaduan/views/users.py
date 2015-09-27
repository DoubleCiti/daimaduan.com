# coding: utf-8
from daimaduan.bootstrap import app
from daimaduan.bootstrap import login
from bottle import request
from bottle import redirect
from bottle import abort
from bottle import jinja2_view

from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

from daimaduan.models import User

from daimaduan.forms import SignupForm
from daimaduan.forms import SigninForm


@app.get('/signin')
@jinja2_view('signin.html')
def signin_get():
    return {'form': SigninForm()}


@app.post('/signin')
@jinja2_view('signin.html')
def signin_post():
    form = SigninForm(request.POST)
    if form.validate():
        login.login_user(str(form.user.id))
        redirect('/')
    else:
        return locals();


@app.delete('/signout')
def signout_delete():
    login.logout_user()
    request.environ.get('beaker.session').delete()
