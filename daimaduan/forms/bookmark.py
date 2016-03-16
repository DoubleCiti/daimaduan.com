# coding: utf-8
from flask_wtf import Form
from wtforms import StringField, BooleanField


class BookmarkForm(Form):
    title = StringField(u'名字')
    description = StringField(u'描述')
    is_private = BooleanField(u'我想要这个码单私有')
