# coding: utf-8
import json
import datetime

from bottle import request
from bottle import redirect
from bottle import abort
from bottle import jinja2_view

from bottle_utils.csrf import csrf_protect
from bottle_utils.csrf import csrf_token

from daimaduan.bootstrap import app
from daimaduan.bootstrap import login
from daimaduan.bootstrap import oauth_services

from daimaduan.models import User
from daimaduan.models import UserOauth
from daimaduan.models import Paste
from daimaduan.models import Tag

from daimaduan.forms import SignupForm
from daimaduan.forms import SigninForm
from daimaduan.forms import EmailForm
from daimaduan.forms import PasswordForm
from daimaduan.forms import UserInfoForm

from daimaduan.utils import user_bind_oauth, jsontify
from daimaduan.utils import get_session

from daimaduan.utils import validate_token
from daimaduan.utils import send_confirm_email
from daimaduan.utils import send_reset_password_email
from daimaduan.utils import logger


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
@jinja2_view('user/manage.html')
@csrf_token
def oauth_callback(provider):
    logger.info("Oauth callback for %s" % provider)
    redirect_uri = app.config['oauth.%s.callback_url' % provider]
    oauth_service = oauth_services[provider]

    data = dict(code=request.params.get('code'),
                grant_type='authorization_code',
                redirect_uri=redirect_uri)

    if provider == 'google':
        oauth_session = oauth_service.get_auth_session(data=data, decoder=json.loads)
        user_info = oauth_session.get('userinfo').json()
        email = user_info['email']
        username = user_info['given_name']
    elif provider == 'github':
        oauth_session = oauth_service.get_auth_session(data=data)
        user_info = oauth_session.get('user').json()
        email = user_info['email']
        username = user_info['login']

    access_token = oauth_session.access_token
    user_info['id'] = str(user_info['id'])

    logger.info("%s oauth access token is: %s" % (provider, access_token))
    logger.info("%s oauth user info is %s" % (provider, user_info))

    user = User.find_by_oauth(provider, user_info['id'])
    if user:
        # TODO: 直接登录时更新 token.
        login.login_user(str(user.id))
        return redirect('/')
    else:
        user = User.objects(email=email).first()
        if user:
            user_oauth = UserOauth(provider=provider, openid=user_info['id'], token=access_token)
            user_oauth.save()
            login.login_user(str(user.id))
            return redirect('/')
        else:
            return {'form': UserInfoForm(email=email, username=username), 'token': request.csrf_token}


@app.post('/user/manage', name='users.manage')
@jinja2_view('user/manage.html')
@csrf_token
@csrf_protect
def manage():
    form = UserInfoForm(request.forms)
    if form.validate():
        if request.user:
            request.user.username = form.username.data
            return redirect('/')
        else:
            user = User(email=form.email.data, username=form.username.data,
                        is_email_confirmed=True)
            user.save()
            login.login_user(str(user.id))
            return redirect('/')
    return {'form': form, 'token': request.csrf_token}


@app.get('/signin', name='users.signin')
@jinja2_view('user/signin.html')
@csrf_token
def signin_get():
    if request.user:
        redirect('/')
    else:
        return {'form': SigninForm(), 'token': request.csrf_token}


@app.post('/signin', name='users.signin')
@jinja2_view('user/signin.html')
@csrf_protect
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
@jinja2_view('user/signup.html')
@csrf_token
def signup_get():
    if request.user:
        redirect('/')
    else:
        return {'form': SignupForm(), 'token': request.csrf_token}


@app.post('/signup', name='users.signup')
@jinja2_view('user/signup.html')
@csrf_token
@csrf_protect
def signup_post():
    form = SignupForm(request.forms)
    if form.validate():
        user = User()
        form.populate_obj(user)
        user.save()
        login.login_user(user.id)
        send_confirm_email(app.config, user.email)
        return redirect('/active_email')
    return {'form': form, 'token': request.csrf_token}


@app.get('/lost_password', name='users.lost_password')
@jinja2_view('user/lost_password.html')
def lost_password_get():
    return {'form': EmailForm()}


@app.post('/lost_password', name='users.lost_password')
@jinja2_view('user/lost_password.html')
def lost_password_post():
    form = EmailForm(request.forms)
    if form.validate():
        user = User.objects(email=form.email.data).first()
        send_reset_password_email(app.config, user.email)
        return redirect('/reset_password_email_sent')
    return {'form': form}


@app.get('/reset_password_email_sent')
@jinja2_view('error.html')
def reset_password_email_sent():
    return {'title': u"重置密码的邮件已经发出", 'message': u"重置密码的邮件已经发出, 请查收邮件并重置密码"}


@app.get('/reset_password/<token>')
@jinja2_view('user/reset_password.html')
def reset_password_get(token):
    email = validate_token(app.config, token)
    if email:
        user = User.objects(email=email).first()
        if user:
            return {'form': PasswordForm(), 'token': token}
    abort(404)


@app.post('/reset_password/<token>')
@jinja2_view('user/reset_password.html')
def reset_password_post(token):
    email = validate_token(app.config, token)
    if email:
        user = User.objects(email=email).first()
        if user:
            form = PasswordForm(request.forms)
            if form.validate():
                user.password = user.generate_password(form.password.data)
                user.save()
                redirect('/reset_password_success')
            return {'form': PasswordForm(), 'token': token}
    abort(404)


@app.get('/reset_password_success')
@jinja2_view('error.html')
def reset_password_success():
    return {'title': u"重置密码成功", 'message': u"您的密码已经重置, 请重新登录"}


@app.get('/user/<username>')
@jinja2_view('user/user.html')
def user_index(username):
    user = User.objects(username=username).first()
    if user:
        if request.user:
            pastes = Paste.objects(user=user).order_by('-updated_at')
        else:
            pastes = Paste.objects(user=user, is_private=False).order_by('-updated_at')
        return {'user': user, 'pastes': pastes}
    return abort(404)


@app.get('/user/favourites', name='users.favourites')
@login.login_required
@jinja2_view('user/favourites.html')
def favourites_get():
    return {'pastes': request.user.get_favourites_by_page(1),
            'tags': Tag.objects().order_by('-popularity')[:10]}


@app.get('/user/favourites/more')
@login.login_required
@jinja2_view('pastes/pastes.html')
def favourites_more():
    p = int(request.query.p)
    if not p:
        return {}
    return {'pastes': request.user.get_favourites_by_page(p)}


@app.get('/confirm/<token>')
@jinja2_view('email/confirm.html')
def confirm_email(token):
    email = validate_token(app.config, token)
    if email:
        user = User.objects(email=email).first()
        if user:
            if (request.user is not None and user == request.user) or request.user is None:
                if user.is_email_confirmed:
                    return {'title': u"Email已经激活过了", 'message': u"对不起，您的email已经激活过了。"}
                else:
                    user.is_email_confirmed = True
                    user.email_confirmed_on = datetime.datetime.now()
                    user.save()
                    return {'title': u'Email已经激活', 'message': u'您的email已经激活，请点击登录查看最新代码段。'}
    return {'title': u'Email验证链接错误', 'message': u'对不起，您的验证链接无效或者已经过期。'}


@app.get('/active_email')
@jinja2_view('email/active.html')
def active_email():
    return {'email': request.user.email, 'title': u'注册成功'}


@app.get('/sendmail/<email>')
@jinja2_view('email/active.html')
def send_mail(email):
    user = User.objects(email=email).first()
    if user:
        if user.is_email_confirmed is False:
            if request.user is None or request.user.email == user.email:
                send_confirm_email(app.config, email)
                return {'title': u'发送成功'}
    return abort(404)
