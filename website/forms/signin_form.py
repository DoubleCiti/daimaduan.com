# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from models import User

class SigninForm(Form):
    email = StringField(u'email')
    password = PasswordField(u'password')

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.objects(email=self.email.data).first()

        if user is None:
            self.password.errors.append('用户名或密码错误')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('用户名或密码错误')
            return False

        self.user = user

        return True