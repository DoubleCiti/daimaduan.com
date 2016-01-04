from daimaduan.models import UserOauth


def oauth_config(config, provider):
    return {
        'name': config['oauth.%s.name' % provider],
        'client_id': config['oauth.%s.client_id' % provider],
        'client_secret': config['oauth.%s.client_secret' % provider],
        'authorize_url': config['oauth.%s.authorize_url' % provider],
        'access_token_url': config['oauth.%s.access_token_url' % provider],
        'base_url': config['oauth.%s.base_url' % provider]
    }


def user_bind_oauth(user, session):
    """Bind oauth info in session to given user, then clear the session"""
    oauth = UserOauth(user=user,
                      provider=session['oauth_provider'],
                      openid=session['oauth_openid'],
                      token=session['oauth_token'])
    oauth.save()

    # Clear oauth info in session
    del session['oauth_provider']
    del session['oauth_openid']
    del session['oauth_name']
    del session['oauth_token']
