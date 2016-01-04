import mongoengine

from daimaduan.models import BaseDocument, User, Paste


class Rate(BaseDocument):
    user = mongoengine.ReferenceField(User)
    paste = mongoengine.ReferenceField(Paste)
    score = mongoengine.IntField(default=0)
