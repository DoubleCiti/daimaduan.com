# coding: utf-8
from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument


class Bookmark(BaseDocument):
    user = db.ReferenceField('User')

    hash_id = db.StringField(unique=True)
    title = db.StringField(required=True)
    description = db.StringField()
    is_private = db.BooleanField(default=False)
    is_default = db.BooleanField(default=False)

    pastes = db.ListField(db.ReferenceField('Paste'))

    def save(self, *args, **kwargs):
        self.create_hash_id(self.user.salt, 'bookmark')
        if not self.title:
            self.title = u"收藏夹: %s" % self.hash_id
        super(Bookmark, self).save(*args, **kwargs)
