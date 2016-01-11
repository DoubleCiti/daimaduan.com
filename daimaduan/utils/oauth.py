from daimaduan.models.user_oauth import UserOauth


def oauth_config(config, provider):
    return {
        'name': config['OAUTH'][provider]['name'],
        'base_url': config['OAUTH'][provider]['base_url'],
        'authorize_url': config['OAUTH'][provider]['authorize_url'],
        'access_token_url': config['OAUTH'][provider]['access_token_url'],
        'client_id': config['OAUTH'][provider]['client_id'],
        'client_secret': config['OAUTH'][provider]['client_secret'],
        # 'callback_url': config['OAUTH'][provider]['callback_url'],
        # 'scope': config['OAUTH'][provider]['scope']
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
