# coding: utf-8
import json

from bottle import request
from bottle import redirect
from bottle import abort
from bottle import jinja2_view

from daimaduan.bootstrap import app
from daimaduan.bootstrap import login
from daimaduan.bootstrap import oauth_services
from daimaduan.bootstrap import logger

from daimaduan.models import User
from daimaduan.models import Paste
from daimaduan.models import Tag

from daimaduan.forms import SignupForm
from daimaduan.forms import SigninForm

from daimaduan.utils import user_bind_oauth, jsontify
from daimaduan.utils import get_session


@app.get('/oauth/<provider>', name='oauth.signin')
def oauth_signin(provider):
    oauth_service = oauth_services[provider]
    redirect_uri = app.config['oauth.%s.callback_url' % provider]
    scope = app.config['oauth.%s.scope' % provider]

    url = oauth_service.get_authorize_url(scope=scope,
                                          response_type='code',
                                          redirect_uri=redirect_uri)
    redirect(url)


@app.route('/oauth/<provider>/callback', name='oauth.callback')
@jinja2_view('oauths/callback.html')
def oauth_callback(provider):
    logger.info("Oauth callback for %s" % provider)
    redirect_uri = app.config['oauth.%s.callback_url' % provider]
    oauth_service = oauth_services[provider]
    session = get_session(request)

    data = dict(code=request.params.get('code'),
                grant_type='authorization_code',
                redirect_uri=redirect_uri)

    if provider == 'google':
        oauth_session = oauth_service.get_auth_session(data=data, decoder=json.loads)
        user_info = oauth_session.get('userinfo').json()
    elif provider == 'weibo':
        access_token = oauth_session.access_token
        oauth_session = oauth_service.get_auth_session(data=data, decoder=json.loads)
        access_token = oauth_session.access_token
        user_info = oauth_session.get('account/get_uid.json').json()
        print '-------------'
        print user_info
        print '-------------'
    else:
        oauth_session = oauth_service.get_auth_session(data=data)
        user_info = oauth_session.get('user').json()

    logger.info("%s oauth user info is %s" % (provider, user_info))

    access_token = oauth_session.access_token
    user_info['id'] = str(user_info['id'])
    logger.info("%s oauth access token is: %s" % (provider, access_token))

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
        pastes = Paste.objects(user=user, is_private=False).order_by('-updated_at')
        return {'user': user, 'pastes': pastes}
    return abort(404)


@app.get('/user/favourites', name='users.favourites')
@login.login_required
@jinja2_view('favourites.html')
def favourites_get():
    return {'pastes': request.user.get_favourites_by_page(1),
            'tags': Tag.objects().order_by('-popularity')[:10]}


@app.get('/user/favourites/more')
@login.login_required
@jsontify
def favourites_more():
    p = int(request.query.p)
    if not p:
        return {}
    return {'pastes': [paste.to_json() for paste in request.user.get_favourites_by_page(p)]}
