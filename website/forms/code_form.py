# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import TextAreaField


class CodeForm(Form):
    title = StringField(u'title')
    content = TextAreaField(u'content')
