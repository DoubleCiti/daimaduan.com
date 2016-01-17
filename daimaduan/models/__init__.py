import datetime
import hashlib
import time

from flask_login import UserMixin

from daimaduan.bootstrap import db


class BaseDocument(db.Document):
    meta = {'abstract': True,
            'strict': False}

    # Increase specific counter by `count`
    def increase_counter(self, field, count=1):
        counter_field = '%s_count' % field
        counter_value = getattr(self, counter_field, 0) + count
        if counter_value <= 0:
            counter_value = 0

        attributes = dict([(counter_field, counter_value)])
        self.update(**attributes)

    @classmethod
    def find_or_create_by(cls, **attributes):
        record = cls.objects(**attributes).first()
        if record is None:
            record = cls(**attributes).save()

        return record

    @classmethod
    def find_and_delete_by(cls, **attributes):
        record = cls.objects(**attributes).first()
        if record:
            record.delete()

    def create_hash_id(self, salt, string):
        if not self.hash_id:
            def generate_hash_id():
                return hashlib.sha1('%s%s%s' % (salt, string, str(time.time()))).hexdigest()[:11]
            self.hash_id = generate_hash_id()
            while(self.__class__.objects(hash_id=self.hash_id).first() is not None):
                self.hash_id = generate_hash_id()

    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)


class LoginManagerUser(UserMixin):
    def __init__(self, user):
        self.user = user
        self.id = user.id
        self.username = user.username
        self.email = user.email
