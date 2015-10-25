# coding: utf-8
import json

from bottle import request
from bottle import redirect
from bottle import abort
from bottle import jinja2_view

from daimaduan.bootstrap import app
from daimaduan.bootstrap import login
from daimaduan.bootstrap import oauth_google
from daimaduan.bootstrap import logger

from daimaduan.models import User
from daimaduan.models import Paste
from daimaduan.models import Tag

from daimaduan.forms import SignupForm
from daimaduan.forms import SigninForm

from daimaduan.utils import user_bind_oauth
from daimaduan.utils import get_session


@app.get('/oauth/<provider>', name='oauth.signin')
def oauth_signin(provider):
    redirect_url = app.config['oauth.google.callback_url']
    url = oauth_google.get_authorize_url(scope='email profile',
                                         response_type='code',
                                         redirect_uri=redirect_url)
    redirect(url)


@app.route('/oauth/<provider>/callback', name='oauth.callback')
@jinja2_view('oauths/callback.html')
def oauth_callback(provider):
    session = get_session(request)

    data = dict(code=request.params.get('code'),
                grant_type='authorization_code',
                redirect_uri=app.config['oauth.google.callback_url'])
    oauth_session = oauth_google.get_auth_session(data=data, decoder=json.loads)

    access_token = oauth_session.access_token
    logger.info("%s oauth access token is: %s" % (provider, access_token))

    user_info = oauth_session.get('userinfo').json()
    logger.info('%s oauth user info is: %s' % (provider, user_info))

    user = User.find_by_oauth(provider, user_info['id'])
    if user:
        # TODO: 直接登录时更新 token.
        login.login_user(str(user.id))
        return redirect('/')
    else:
        session['oauth_provider'] = provider
        session['oauth_openid'] = user_info['id']
        session['oauth_name'] = user_info['name']
        session['oauth_token'] = access_token
        session.save()

        return {'user_info': user_info}


@app.get('/signin', name='users.signin')
@jinja2_view('signin.html')
def signin_get():
    if request.user:
        redirect('/')
    else:
        return {'form': SigninForm()}


@app.post('/signin', name='users.signin')
@jinja2_view('signin.html')
def signin_post():
    session = get_session(request)

    form = SigninForm(request.POST)
    if form.validate():
        login.login_user(str(form.user.id))

        if 'oauth_provider' in session:
            user_bind_oauth(form.user, session)

        redirect('/')
    else:
        return locals()


@app.delete('/signout', name='users.signout')
def signout_delete():
    login.logout_user()
    request.environ.get('beaker.session').delete()


@app.get('/signup', name='users.signup')
@jinja2_view('signup.html')
def signup_get():
    if request.user:
        redirect('/')
    else:
        return {'form': SignupForm()}


@app.post('/signup', name='users.signup')
@jinja2_view('signup.html')
def signup_post():
    form = SignupForm(request.forms)
    if form.validate():
        user = User()
        form.populate_obj(user)
        user.save()

        return redirect('/signin')
    return {'form': form}


@app.get('/user/<username>')
@jinja2_view('user.html')
def user_index(username):
    user = User.objects(username=username).first()
    if user:
        pastes = Paste.objects(user=user).order_by('-updated_at')
        return {'user': user, 'pastes': pastes}
    return abort(404)


@app.get('/user/favourites')
@jinja2_view('favourites.html')
def favourites_get():
    return {'pastes': request.user.favourites,
            'tags': Tag.objects().order_by('-popularity')[:10]}
