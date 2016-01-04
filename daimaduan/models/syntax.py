import mongoengine

from daimaduan.models import BaseDocument


class Syntax(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)
