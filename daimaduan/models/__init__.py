# https://github.com/MongoEngine/flask-mongoengine/blob/master/flask_mongoengine/__init__.py
import datetime
import hashlib
import time

import mongoengine
from bottle import abort
from mongoengine.base import ValidationError
from mongoengine.queryset import DoesNotExist
from mongoengine.queryset import MultipleObjectsReturned
from mongoengine.queryset import QuerySet


# https://github.com/MongoEngine/flask-mongoengine/blob/master/flask_mongoengine/__init__.py
class BaseQuerySet(QuerySet):
    """
    A base queryset with handy extras
    """

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except (MultipleObjectsReturned, DoesNotExist, ValidationError):
            abort(404)

    def first_or_404(self):

        obj = self.first()
        if obj is None:
            abort(404)

        return obj


class BaseDocument(mongoengine.Document):
    meta = {'abstract': True,
            'strict': False,
            'queryset_class': BaseQuerySet}

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

    created_at = mongoengine.DateTimeField(default=datetime.datetime.now)
    updated_at = mongoengine.DateTimeField(default=datetime.datetime.now)
