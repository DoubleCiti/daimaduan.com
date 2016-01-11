# coding: utf-8
from flask_wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from daimaduan.models.base import User


class SigninForm(Form):
    email = StringField(u'email', validators=[InputRequired()])
    password = PasswordField(u'password', validators=[InputRequired()])

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.objects(email=self.email.data).first()

        if user:
            if user.check_login(self.password.data):
                self.user = user
                return True

        self.password.errors.append(u'登录邮箱或者密码不正确')
        return False
