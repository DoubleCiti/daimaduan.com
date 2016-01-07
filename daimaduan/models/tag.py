import mongoengine

from daimaduan.models import BaseDocument
from daimaduan.models.base import Paste


class Tag(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)
    popularity = mongoengine.IntField(default=1)

    @property
    def pastes(self):
        return Paste.objects(tags=self.name)
