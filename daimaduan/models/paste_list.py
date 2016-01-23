# coding: utf-8
from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument
from daimaduan.models.base import User


class PasteList(BaseDocument):
    user = db.ReferenceField(User)

    hash_id = db.StringField(unique=True)
    title = db.StringField(required=True)
    description = db.StringField()
    is_private = db.BooleanField(default=False)

    pastes = db.ListField(db.ReferenceField('Paste'))

    def save(self, *args, **kwargs):
        self.create_hash_id(self.user.salt, 'paste_list')
        if not self.title:
            self.title = u"码单: %s" % self.hash_id
        super(PasteList, self).save(*args, **kwargs)
