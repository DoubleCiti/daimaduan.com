from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument


class Syntax(BaseDocument):
    name = db.StringField(required=True, unique=True)
