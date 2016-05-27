# coding: utf-8
import json

from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app
from flask import abort
from flask import redirect
from flask import session

from rauth import OAuth2Service

from daimaduan.models.base import User
from daimaduan.models.user_oauth import UserOauth
from daimaduan.extensions.log import get_logger

oauth_app = Blueprint("oauth_app", __name__, template_folder="templates")
logger = get_logger()


def oauth_for(provider):
    try:
        config = current_app.config['OAUTH'][provider]
        service = OAuth2Service(client_id=config['client_id'],
                                client_secret=config['client_secret'],
                                name=config['name'],
                                access_token_url=config['access_token_url'],
                                authorize_url=config['authorize_url'],
                                base_url=config['base_url'])
        return config, service
    except KeyError:
        logger.warn('Not supported oauth provider: %s', provider)
        abort(404)


@oauth_app.route('/<provider>', methods=['GET'])
def oauth_signin(provider):
    logger.info('Request for %s authorization' % provider)
    config, service = oauth_for(provider)
    url = service.get_authorize_url(response_type='code',
                                    redirect_uri=config['callback_url'],
                                    scope=config['scope'])
    logger.info("Redirect to %s" % url)
    return redirect(url)


@oauth_app.route('/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    logger.info("Oauth callback for %s" % provider)
    config, service = oauth_for(provider)
    data = dict(code=request.args.get('code'),
                grant_type='authorization_code',
                redirect_uri=config['callback_url'])

    if provider == 'google':
        api = service.get_auth_session(data=data, decoder=json.loads)
        user_info = api.get('userinfo').json()
        email = session['email'] = user_info['email']
        username = user_info['given_name']
    elif provider == 'github':
        api = service.get_auth_session(data=data)
        user_info = api.get('user').json()
        email = session['email'] = user_info['email']
        username = user_info['login']
    elif provider == 'weibo':
        api = service.get_auth_session(data=data, decoder=json.loads)
        
        payload = {'access_token': api.access_token}

        uid = api.get('account/get_uid.json', params=payload).json()['uid']
        email = api.get('account/profile/email.json', params=payload).json()
        email = session['email'] = ''

        payload['uid'] = uid
        user_info = api.get('users/show.json', params=payload).json()
        username = user_info['name']

    access_token = api.access_token
    user_info['id'] = str(user_info['id'])

    user = User.find_by_oauth(provider, user_info['id'])
    if user:
        # TODO: 直接登录时更新 token.
        user_mixin = LoginManagerUser(user)
        login_user(user_mixin)
        flash(u"登录成功", category='info')
        return redirect('/')
    else:
        user = User.objects(email=email).first()
        if user:
            user_oauth = UserOauth(provider=provider, openid=user_info['id'], token=access_token)
            user_oauth.save()
            user_mixin = LoginManagerUser(user)
            login_user(user_mixin)
            flash(u"登录成功", category='info')
            return redirect('/')
        else:
            return render_template('users/finish_signup.html',
                                   form=UserInfoForm(email=email, username=username))