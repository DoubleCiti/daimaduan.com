# coding: utf-8

"""
Signup Form
"""

from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import ValidationError
from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Regexp
from models import User

class SignupForm(Form):
    username = StringField(u'username', validators=[
        InputRequired(), Regexp(r'\S{3,50}', message=u'至少3个字符，不能包含空格')])
    email = StringField(u'email', validators=[InputRequired(), Email()])
    password = PasswordField(u'password', validators=[InputRequired()])

    def validate_username(self, field):
        user = User.objects(username=field.data).first()
        if user is not None:
            raise ValidationError(u'用户名已被使用')

    def validate_email(self, field):
        user = User.objects(email=field.data).first()
        if user is not None:
            raise ValidationError(u'Email 已被使用')
