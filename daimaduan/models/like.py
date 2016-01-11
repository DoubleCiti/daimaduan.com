from mongoengine import signals

from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument


class Like(BaseDocument):
    user = db.ReferenceField('User')
    likeable = db.ReferenceField('Paste')

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created'):
            field = document.likeable._cls.lower()
            document.user.increase_counter('%s_likes' % field)
            document.likeable.increase_counter('likes')

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        field = document.likeable._cls.lower()
        document.user.increase_counter('%s_likes' % field, -1)
        document.likeable.increase_counter('likes', -1)

signals.post_save.connect(Like.post_save, sender=Like)
signals.post_delete.connect(Like.post_delete, sender=Like)
