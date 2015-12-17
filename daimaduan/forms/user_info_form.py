# coding: utf-8
from bottle import request

from wtforms import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Regexp

from daimaduan.models import User
from daimaduan.utils import get_session


class UserInfoForm(Form):
    username = StringField(u'昵称', validators=[
        InputRequired(), Regexp(r'\S{3,12}', message=u'3到12个字符，不能包含空格')])
    email = StringField(u'Email', validators=[InputRequired(), Email()])

    def validate_username(self, field):
        user = User.objects(username=field.data).first()
        if user:
            raise ValidationError(u'用户名已被使用')

    def validate_email(self, field):
        session = get_session(request)
        if session['email']:
            if session['email'] != field.data:
                raise ValidationError(u'不能修改第三方登录的email地址')
        user = User.objects(email=field.data).first()
        if user:
            raise ValidationError(u'Email地址已被使用')
