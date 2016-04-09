# coding: utf-8
from flask_wtf import Form
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms.validators import EqualTo


class PasswordForm(Form):
    password = PasswordField(u'密码', validators=[InputRequired()])
    password_confirm = PasswordField(u'密码确认', validators=[EqualTo('password', message=u'两次密码不同')])
