# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import FieldList
from wtforms import FormField
from wtforms.validators import InputRequired


class CodeForm(Form):
    title = StringField(u'片段描述', validators=[InputRequired()])
    content = TextAreaField(u'代码片段', validators=[InputRequired()])


class PasteForm(Form):
    title = StringField(u'标题', validators=[InputRequired()])
    codes = FieldList(FormField(CodeForm))
