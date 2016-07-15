from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument
from daimaduan.models.base import Paste


class Tag(BaseDocument):
    key = db.StringField(required=True, unique=True)
    name = db.StringField(required=True, unique=True)
    popularity = db.IntField(default=1)

    def __unicode__(self):
        return "<Tag:%s>" % self.name
