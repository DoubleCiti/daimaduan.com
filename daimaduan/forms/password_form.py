# coding: utf-8
from wtforms import Form
from wtforms import PasswordField
from wtforms.validators import InputRequired


class PasswordForm(Form):
    password = PasswordField(u'password', validators=[InputRequired()])
