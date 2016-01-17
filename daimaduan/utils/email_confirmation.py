# coding: utf-8
from itsdangerous import URLSafeTimedSerializer

from daimaduan.models.base import User
from daimaduan.tasks.celery import send_email


CONFIRMATION_SUBJECT = u'请激活您在代码段注册的邮箱地址'
CONFIRMATION_CONTENT = u"<p>你好 %s,</p> \
    <p>非常感谢注册代码段. 请点击<a href=\"https://%s/confirm/%s\">链接</a>来激活您的邮箱地址.</p> \
            <p>或者您可以拷贝下面这个地址到您的浏览器中访问来激活邮箱地址 https://%s/confirm/%s </p> \
            <br> \
            <p>此致！</p> \
            <p>代码段团队</p>"
RESET_PASSWORD_SUBJECT = u'您请求重置密码'
RESET_PASSWORD_CONTENT = u"<p>你好 %s,</p> \
    <p>您已请求重置代码段密码. 请点击<a href=\"https://%s/reset_password/%s\">链接</a>来重置您的密码.</p> \
            <p>或者您可以拷贝下面这个地址到您的浏览器中访问来重置您的密码 https://%s/reset_password/%s </p> \
            <br> \
            <p>此致！</p> \
            <p>代码段团队</p>"


def get_email_config(config):
    return dict(host=config['EMAIL']['host'],
                port=config['EMAIL']['port'],
                username=config['EMAIL']['username'],
                password=config['EMAIL']['password'])


def generate_confirmation_token(config, email):
    """generate confirmation token using user's email via itsdangerous"""
    serializer = URLSafeTimedSerializer(config['SECRET_KEY'])
    return serializer.dumps(email, salt=config['EMAIL']['salt'])


def validate_token(config, token, expire_time=3600):
    """from token and expire_time to confirm user's email"""
    serializer = URLSafeTimedSerializer(config['SECRET_KEY'])
    try:
        confirmed_email = serializer.loads(token, max_age=expire_time, salt=config['EMAIL']['salt'])
    except Exception:
        return False
    return confirmed_email


def send_confirm_email(config, user_email):
    token = generate_confirmation_token(config, user_email)
    user = User.objects(email=user_email).first()
    content = CONFIRMATION_CONTENT % (user.username, config['DOMAIN'], token, config['DOMAIN'], token)
    send_email.delay(get_email_config(config), user_email, CONFIRMATION_SUBJECT, content)


def send_reset_password_email(config, user_email):
    token = generate_confirmation_token(config, user_email)
    user = User.objects(email=user_email).first()
    content = RESET_PASSWORD_CONTENT % (user.username, config['DOMAIN'], token, config['DOMAIN'], token)
    send_email.delay(get_email_config(config), user_email, RESET_PASSWORD_SUBJECT, content)
