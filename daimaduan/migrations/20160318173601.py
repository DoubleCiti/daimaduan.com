# coding: utf-8
import hashlib

import time

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        """
        Add default bookmark to every user
        :return:
        """
        user_ids = [str(i['user']) for i in self.db.bookmark.find()]
        users = self.db.user.find()
        for user in users:
            if str(user['_id']) not in user_ids:
                self.db.bookmark.save({'user': user['_id'],
                                       'title': u'%s 的收藏夹' % user['username'],
                                       'description': '',
                                       'hash_id': self.create_hash_id(user['salt'], 'bookmark'),
                                       'created_at': user['created_at'],
                                       'updated_at': user['created_at'],
                                       'pastes': [],
                                       'is_private': False,
                                       'is_default': True})

    def create_hash_id(self, salt, string):
        def generate_hash_id():
            return hashlib.sha1('%s%s%s' % (salt, string, str(time.time()))).hexdigest()[:11]
        hash_id = generate_hash_id()
        while(self.db.bookmark(hash_id=hash_id).first() is not None):
            hash_id = generate_hash_id()

        return hash_id

    def downgrade(self):
        print "I'm in downgrade - migration2"
