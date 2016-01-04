import mongoengine

from daimaduan.models import BaseDocument


class UserOauth(BaseDocument):
    user = mongoengine.ReferenceField('User')

    provider = mongoengine.StringField(required=True)
    openid = mongoengine.StringField(required=True)
    token = mongoengine.StringField(required=True)
