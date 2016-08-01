# coding: utf-8

from wtforms import Form
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import FieldList
from wtforms import FormField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError


class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass


class CodeForm(Form):
    title = StringField(u'片段描述')
    syntax = NonValidatingSelectField(u'语法')
    content = TextAreaField(u'代码片段',
                            validators=[
                                DataRequired(message=u'不能为空！')
                            ])


class PasteForm(Form):
    title = StringField(u'标题')
    is_private = BooleanField(u'我想要这段代码私有')
    codes = FieldList(FormField(CodeForm), min_entries=1, max_entries=7)
    tags = StringField(u'标签')

    def validate(self):
        if not Form.validate(self):
            return False

        if self.tags.data and len(self.tags.data.split(' ')) > 3:
            self.tags.errors.append(u'只能输入3个标签')
            return False

        return True


class CommentForm(Form):
    content = StringField(u'评论')
