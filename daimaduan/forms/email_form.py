# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms.validators import Email
from daimaduan.models import User


class EmailForm(Form):
    email = StringField(u'email', validators=[InputRequired(), Email(message=u"邮件地址不正确")])

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.objects(email=self.email.data).first()

        if not user:
            self.email.errors.append(u'用户不存在')
            return False

        return True
