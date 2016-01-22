# coding: utf-8
from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import InputRequired


class PasteListForm(Form):
    title = StringField(u'名字', validators=[InputRequired()])
    description = StringField(u'描述')
    is_private = BooleanField(u'我想要这个码单私有')
