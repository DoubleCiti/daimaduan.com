# coding=utf-8
from functools import wraps
from json import dumps

from bottle import request, jinja2_template, response
from bottle_utils.csrf import generate_csrf_token


def user_active_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.user.is_email_confirmed:
            return func(*args, **kwargs)
        generate_csrf_token()
        return jinja2_template('email/active.html', email=request.user.email, title=u"邮箱需要激活", reactive=True, token=request.csrf_token)
    return wrapper


def jsontify(func):
    @wraps(func)
    def jsontify_function(*args, **kwargs):
        result = func(*args, **kwargs)
        response.content_type = 'application/json'
        return dumps(result)
    return jsontify_function
