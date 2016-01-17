# coding=utf-8
from functools import wraps
from json import dumps

from bottle import request, jinja2_template, response
from bottle_utils.csrf import generate_csrf_token
from flask import render_template
from flask_login import current_user

from daimaduan.forms.email import EmailForm


def user_active_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.user.is_email_confirmed:
            return func(*args, **kwargs)
        form = EmailForm()
        return render_template('email/active.html',
                               title=u"邮箱需要激活",
                               reactive=True,
                               form=form)
    return wrapper


def jsontify(func):
    @wraps(func)
    def jsontify_function(*args, **kwargs):
        result = func(*args, **kwargs)
        response.content_type = 'application/json'
        return dumps(result)
    return jsontify_function
