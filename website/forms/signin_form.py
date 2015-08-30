# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from models import User

class SigninForm(Form):
    email = StringField(u'email', validators=[InputRequired()])
    password = PasswordField(u'password', validators=[InputRequired()])

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.objects(email=self.email.data).first()

        if user is None:
            self.password.errors.append(u'登录邮箱或者密码不正确')
            return False

        if not user.check_login(self.password.data):
            self.password.errors.append(u'登录邮箱或者密码不正确')
            return False

        self.user = user

        return True