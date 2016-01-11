from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument
from daimaduan.models.base import Paste


class Tag(BaseDocument):
    name = db.StringField(required=True, unique=True)
    popularity = db.IntField(default=1)

    @property
    def pastes(self):
        return Paste.objects(tags=self.name)
