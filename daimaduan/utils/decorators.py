# coding=utf-8
from functools import wraps

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
