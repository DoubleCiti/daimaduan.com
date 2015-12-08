# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import ValidationError
from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Regexp
from daimaduan.models import User


class UserInfoForm(Form):
    username = StringField(u'昵称', validators=[
        InputRequired(), Regexp(r'\S{3,12}', message=u'3到12个字符，不能包含空格')])
    email = StringField(u'Email', validators=[InputRequired(), Email()])

    def validate_username(self, field):
        user = User.objects(username=field.data).first()
        if user is not None:
            raise ValidationError(u'用户名已被使用')
