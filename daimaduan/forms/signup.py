# coding: utf-8
from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import ValidationError
from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Regexp
from wtforms.validators import EqualTo
from daimaduan.models.base import User


class SignupForm(Form):
    username = StringField(u'昵称', validators=[
        InputRequired(), Regexp(r'\S{3,12}', message=u'3到12个字符，不能包含空格')])
    email = StringField(u'Email', validators=[InputRequired(), Email()])
    password = PasswordField(u'密码', validators=[InputRequired()])
    password_confirm = PasswordField(u'密码确认', validators=[EqualTo('password', message=u'两次密码不同')])

    def validate_username(self, field):
        user = User.objects(username=field.data).first()
        if user is not None:
            raise ValidationError(u'用户名已被使用')

    def validate_email(self, field):
        user = User.objects(email=field.data).first()
        if user is not None:
            raise ValidationError(u'Email已被使用')
