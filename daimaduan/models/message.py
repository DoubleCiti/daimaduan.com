# coding: utf-8
import datetime

from daimaduan.bootstrap import db
from daimaduan.models.message_category import NEW_PASTE


CHOICES = [NEW_PASTE]

TITLES = {
    NEW_PASTE: u"新代码集合发布了"
}


class Message(db.Document):
    user = db.ReferenceField('User')
    category = db.StringField(choices=CHOICES)
    content = db.StringField()
    is_read = db.BooleanField(default=False)
    created_at = db.DateTimeField(default=datetime.datetime.now)

    @property
    def title(self):
        return TITLES[self.category]
