# coding: utf-8
import datetime
import time
import hashlib
import mongoengine

from bottle import request
from bottle import abort

from daimaduan.jinja_ext import time_passed
from mongoengine import signals
from mongoengine.base import ValidationError
from mongoengine.queryset import MultipleObjectsReturned
from mongoengine.queryset import DoesNotExist
from mongoengine.queryset import QuerySet
from mongoengine.queryset import queryset_manager


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

    created_at = mongoengine.DateTimeField(default=datetime.datetime.now)
    updated_at = mongoengine.DateTimeField(default=datetime.datetime.now)


class User(BaseDocument):
    username = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField()
    salt = mongoengine.StringField()
    is_email_confirmed = mongoengine.BooleanField(default=False)
    email_confirmed_on = mongoengine.DateTimeField(default=None)

    oauths = mongoengine.ListField(mongoengine.ReferenceField('UserOauth'))

    paste_likes_count = mongoengine.IntField(default=0)
    pastes_count = mongoengine.IntField(default=0)

    @property
    def private_pastes_count(self):
        return len(self.pastes(is_private=True))

    @property
    def public_pastes_count(self):
        return self.pastes_count - len(self.pastes(is_private=True))

    @property
    def likes(self):
        return Like.objects(user=self)

    @property
    def pastes(self):
        return Paste.objects(user=self)

    def save(self, *args, **kwargs):
        if not self.salt:
            self.salt = hashlib.sha1(str(time.time())).hexdigest()
            self.password = self.generate_password(self.password)
        super(User, self).save(*args, **kwargs)

    def owns_record(self, record):
        return record.user == self

    def generate_password(self, string):
        return hashlib.sha1('%s%s' % (string, self.salt)).hexdigest()

    def check_login(self, password):
        return self.generate_password(password) == self.password

    def gravatar_url(self, width=80):
        return "https://cn.gravatar.com/avatar/%s?s=%d" % (hashlib.md5(self.email).hexdigest(), width)

    @classmethod
    def find_by_oauth(cls, provider, openid):
        """Find user that has oauth info with given provider and openid"""

        oauth = UserOauth.objects(provider=provider, openid=openid).first()

        if oauth and oauth.user:
            return oauth.user

    def is_in_favourites(self, paste):
        return paste in self.favourites

    def to_json(self):
        return {'username': self.username,
                'gravatar_url': self.gravatar_url(width=38)}

    def liked(self, paste):
        like = Like.objects(likeable=paste, user=self).first()
        return like is not None


class UserOauth(BaseDocument):
    user = mongoengine.ReferenceField('User')

    provider = mongoengine.StringField(required=True)
    openid = mongoengine.StringField(required=True)
    token = mongoengine.StringField(required=True)


class Code(BaseDocument):
    user = mongoengine.ReferenceField(User)

    hash_id = mongoengine.StringField()
    title = mongoengine.StringField()
    content = mongoengine.StringField(required=True)
    tag = mongoengine.StringField()

    def name(self):
        if len(self.title):
            return self.title
        else:
            return u'代码段: %s' % self.hash_id

    def content_head(self, n=10):
        lines = self.content.splitlines()[:n]
        return '\n'.join(lines)


class Paste(BaseDocument):
    user = mongoengine.ReferenceField(User)

    title = mongoengine.StringField()
    hash_id = mongoengine.StringField()
    is_private = mongoengine.BooleanField(default=False)
    codes = mongoengine.ListField(mongoengine.ReferenceField(Code))
    tags = mongoengine.ListField(mongoengine.StringField())
    rate = mongoengine.IntField(default=0)
    views = mongoengine.IntField(default=0)

    likes_count = mongoengine.IntField(default=0)

    def save(self, *args, **kwargs):
        if not self.hash_id:
            def generate_hash_id():
                return hashlib.sha1('%s%s' % (self.user.salt, str(time.time()))).hexdigest()[:11]
            self.hash_id = generate_hash_id()
            while(Paste.objects(hash_id=self.hash_id).first() is not None):
                self.hash_id = generate_hash_id()
        if not self.title:
            self.title = u'代码集合: %s' % self.hash_id
        super(Paste, self).save(*args, **kwargs)

    def increase_views(self):
        self.views = self.views + 1
        self.save()

    def to_json(self):
        return {'hash_id': self.hash_id,
                'title': self.title,
                'short_title': self.title[:30],
                'tags': self.tags,
                'num_codes': len(self.codes),
                'time_passed': time_passed(self.updated_at),
                'disqus_identifier': self.disqus_identifier,
                'is_private': self.is_private,
                'user': self.user.to_json()}

    def is_user_favourited(self):
        if request.user:
            return request.user.is_in_favourites(self)
        return False

    @property
    def disqus_identifier(self):
        return 'paste-%s' % self.hash_id

    def toggle_like_by(self, user, flag):
        filters = dict(likeable=self, user=user)

        if flag:
            Like.find_or_create_by(**filters)
        else:
            Like.find_and_delete_by(**filters)

        return {
            'paste_id': self.hash_id,
            'user_like': user.reload().paste_likes_count,
            'paste_likes': self.reload().likes_count,
            'liked': flag
        }

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created'):
            document.user.increase_counter('pastes')

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        document.user.increase_counter('pastes', -1)

signals.post_save.connect(Paste.post_save, sender=Paste)
signals.post_delete.connect(Paste.post_delete, sender=Paste)


class Tag(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)
    popularity = mongoengine.IntField(default=1)

    @property
    def pastes(self):
        return Paste.objects(tags=self.name)


class Syntax(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)


class Rate(BaseDocument):
    user = mongoengine.ReferenceField(User)
    paste = mongoengine.ReferenceField(Paste)
    score = mongoengine.IntField(default=0)


class Like(BaseDocument):
    user = mongoengine.ReferenceField('User')
    likeable = mongoengine.GenericReferenceField('Paste')

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
