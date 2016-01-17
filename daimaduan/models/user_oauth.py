from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument


class UserOauth(BaseDocument):
    user = db.ReferenceField('User')

    provider = db.StringField(required=True)
    openid = db.StringField(required=True)
    token = db.StringField(required=True)
