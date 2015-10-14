# coding: utf-8
from wtforms import Form
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import FieldList
from wtforms import FormField
from wtforms import SelectField
from wtforms.validators import InputRequired

from daimaduan.models import Syntax


class CodeForm(Form):
    title = StringField(u'片段描述')
    tag = SelectField(u'语法', choices=[(s.name.lower(), s.name) for s in Syntax.objects()])
    content = TextAreaField(u'代码片段', validators=[InputRequired(message=u'不能为空！')])


class PasteForm(Form):
    title = StringField(u'标题')
    codes = FieldList(FormField(CodeForm))
