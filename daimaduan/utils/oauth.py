from daimaduan.models.user_oauth import UserOauth

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
