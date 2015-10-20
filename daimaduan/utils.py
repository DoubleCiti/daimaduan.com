"""
    daimaduan.utils
    ---------------

    A set of utilities.
"""

from daimaduan.models import UserOauth


def get_session(request):
    """Get session instance from request"""

    return request.environ.get('beaker.session')


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