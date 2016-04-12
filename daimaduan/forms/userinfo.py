# coding: utf-8
from flask import session
from flask.ext.login import current_user
from flask_wtf import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import Email
from wtforms.validators import InputRequired
from wtforms.validators import Regexp

from daimaduan.models.base import User


class UserInfoForm(Form):
    username = StringField(u'昵称', validators=[
        InputRequired(), Regexp(r'^[a-zA-Z0-9-_]{3,12}$', message=u'3到12个字符，不能包含空格')])
    email = StringField(u'邮箱地址', validators=[InputRequired(), Email()])
    description = StringField(u'个性签名', validators=[
        InputRequired(), Regexp(r'^\S{1,20}$', message=u'1到20个字符，不能包含空格')])

    def validate_username(self, field):
        if current_user.is_authenticated and current_user.user.username == field.data:
            return True

        user = User.objects(username=field.data).first()
        if user:
            raise ValidationError(u'用户名已被使用')

    def validate_email(self, field):
        if current_user.is_authenticated:
            field.data = current_user.user.email
            return True

        if session['email']:
            if session['email'] != field.data:
                raise ValidationError(u'不能修改第三方登录的email地址')
        user = User.objects(email=field.data).first()
        if user:
            raise ValidationError(u'Email地址已被使用')
