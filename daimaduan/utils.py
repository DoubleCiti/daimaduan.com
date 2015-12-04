# coding: utf-8

"""
    daimaduan.utils
    ---------------

    A set of utilities.
"""
from bottle import request
from bottle import abort
from functools import wraps
from json import dumps
import logging

from bottle import response
from itsdangerous import URLSafeTimedSerializer
from mailthon import email
from mailthon.postman import Postman
from mailthon.middleware import TLS
from mailthon.middleware import Auth

from daimaduan.models import UserOauth
from daimaduan.models import User

# Setup logger
logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('daimaduan')


def oauth_config(config, provider):
    return {
        'name': config['oauth.%s.name' % provider],
        'client_id': config['oauth.%s.client_id' % provider],
        'client_secret': config['oauth.%s.client_secret' % provider],
        'authorize_url': config['oauth.%s.authorize_url' % provider],
        'access_token_url': config['oauth.%s.access_token_url' % provider],
        'base_url': config['oauth.%s.base_url' % provider]
    }


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


def jsontify(func):
    @wraps(func)
    def jsontify_function(*args, **kwargs):
        result = func(*args, **kwargs)
        response.content_type = 'application/json'
        return dumps(result)
    return jsontify_function


def generate_confirmation_token(config, email):
    """generate confirmation token using user's email via itsdangerous"""
    serializer = URLSafeTimedSerializer(config['site.secret_key'])
    return serializer.dumps(email, salt=config['site.token_salt'])


def validate_token(config, token, expire_time=3600):
    """from token and expire_time to confirm user's email"""
    serializer = URLSafeTimedSerializer(config['site.secret_key'])
    try:
        confirmed_email = serializer.loads(token, max_age=expire_time, salt=config['site.token_salt'])
    except Exception:
        return False
    return confirmed_email


SENDER = 'noreply.daimaduan@gmail.com'
CONFIRMATION_SUBJECT = u'请激活您在代码段注册的邮箱地址'
CONFIRMATION_CONTENT = u"<p>你好 %s,</p> \
    <p>非常感谢注册代码段. 请点击<a href=\"http://daimaduan.com/confirm/%s\">链接</a>来激活您的邮箱地址.</p> \
            <p>或者您可以拷贝下面这个地址到您的浏览器中访问来激活邮箱地址 http://daimaduan.com/confirm/%s </p> \
            <br> \
            <p>此致！</p> \
            <p>代码段团队</p>"
RESET_PASSWORD_SUBJECT = u'您请求重置密码'
RESET_PASSWORD_CONTENT = u"<p>你好 %s,</p> \
    <p>您已请求重置代码段密码. 请点击<a href=\"http://daimaduan.com/reset_password/%s\">链接</a>来重置您的密码.</p> \
            <p>或者您可以拷贝下面这个地址到您的浏览器中访问来重置您的密码 http://daimaduan.com/reset_password/%s </p> \
            <br> \
            <p>此致！</p> \
            <p>代码段团队</p>"


def send_confirm_email(config, user_email):
    token = generate_confirmation_token(config, user_email)
    user = User.objects(email=user_email).first()
    content = CONFIRMATION_CONTENT % (user.username, token, token)
    send_email(config, user_email, CONFIRMATION_SUBJECT, content)


def send_reset_password_email(config, user_email):
    token = generate_confirmation_token(config, user_email)
    user = User.objects(email=user_email).first()
    content = RESET_PASSWORD_CONTENT % (user.username, token, token)
    send_email(config, user_email, RESET_PASSWORD_SUBJECT, content)


def send_email(config, user_email, subject, content):
    envelope = email(
        sender=SENDER,
        receivers=[user_email],
        subject=subject,
        content=content,
    )

    postman = Postman(host=config['mail.host'],
                      port=int(config['mail.port']),
                      middlewares=[TLS(force=True),
                                   Auth(username=config['mail.username'], password=config['mail.password'])])
    try:
        response = postman.send(envelope)
        if response.ok:
            logger.info("Successfully send email to %s" % user_email)
        else:
            logger.error("Failed to send email to %s" % user_email)
    except Exception, e:
        logger.error("Exception occured when send email to %s" % e)


def user_active_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.user.is_email_confirmed:
            return func(*args, **kwargs)
        return abort(403)
    return wrapper
