# coding: utf-8
from wtforms import Form
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms.validators import EqualTo


class PasswordForm(Form):
    password = PasswordField(u'password', validators=[InputRequired()])
    password_confirm = PasswordField(u'密码确认', validators=[EqualTo('password', message=u'两次密码不同')])
