# coding: utf-8
from daimaduan.bootstrap import app
from daimaduan.bootstrap import login
from bottle import request
from bottle import redirect
from bottle import abort
from bottle import jinja2_view

from daimaduan.models import User
from daimaduan.models import Paste

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


@app.get('/signup')
@jinja2_view('signup.html')
def signup_get():
    return {'form': SignupForm()}


@app.post('/signup')
@jinja2_view('signup.html')
def signup_post():
    form = SignupForm(request.forms)
    if form.validate():
        user = User()
        form.populate_obj(user)
        user.save()
        return redirect('/signin')
    return { 'form': form }


@app.get('/user/<username>')
@jinja2_view('user.html')
def user_index(username):
    user = User.objects(username=username).first()
    if user:
        pastes = Paste.objects(user=user).order_by('-updated_at')
        return { 'user': user, 'pastes': pastes}
    return abort(404)
