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
        users = self.db.user.find()
        num = 1
        for user in users:
            user['number'] = num
            user['description'] = u'这个家伙很懒, TA什么都没写...'
            self.db.user.save(user)
            num += 1

    def downgrade(self):
        print "I'm in downgrade - migration2"
