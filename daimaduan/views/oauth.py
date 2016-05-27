# coding: utf-8

from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app
from flask import abort

from rauth import OAuth2Service

from daimaduan.models.user_oauth import UserOauth

oauth_app = Blueprint("oauth_app", __name__, template_folder="templates")

def service_for(provider):
    oauth_config = current_app.config['OAUTH'][provider]

    if oauth_config:
        return OAuth2Service(**oauth_config)
    else:
        abort(404)

@oauth_app.route('/<provider>', methods=['GET'])
def oauth_signin(provider):
    oauth_service = service_for(provider)
    url = oauth_service.get_authorize_url(response_type='code')

    return redirect(url)


@oauth_app.route('/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    current_app.logger.info("Oauth callback for %s" % provider)
    redirect_uri = current_app.config['OAUTH'][provider]['callback_url']
    oauth_service = get_oauth_services()[provider]

    data = dict(code=request.args.get('code'),
                grant_type='authorization_code',
                redirect_uri=redirect_uri)

    if provider == 'google':
        oauth_session = oauth_service.get_auth_session(data=data, decoder=json.loads)
        user_info = oauth_session.get('userinfo').json()
        email = session['email'] = user_info['email']
        username = user_info['given_name']
    elif provider == 'github':
        oauth_session = oauth_service.get_auth_session(data=data)
        user_info = oauth_session.get('user').json()
        email = session['email'] = user_info['email']
        username = user_info['login']
    elif provider == 'weibo':
        oauth_session = oauth_service.get_auth_session(data=data, decoder=json.loads)
        uid = oauth_session.get('account/get_uid.json', params={'access_token': oauth_session.access_token}).json()['uid']
        email = oauth_session.get('account/profile/email.json', params={'access_token': oauth_session.access_token}).json()
        current_app.logger.info("Email: %s" % email)
        user_info = oauth_session.get('users/show.json', params={'access_token': oauth_session.access_token, 'uid': uid}).json()
        email = None
        username = user_info['name']

    access_token = oauth_session.access_token
    user_info['id'] = str(user_info['id'])

    current_app.logger.info("%s oauth access token is: %s" % (provider, access_token))
    current_app.logger.info("%s oauth user info is %s" % (provider, user_info))

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