# coding: utf-8
import hashlib
import time

import mongoengine
from mongoengine import signals
from bottle import request

from daimaduan.extensions.jinja import time_passed
from daimaduan.models import BaseDocument
from daimaduan.models.like import Like
from daimaduan.models.user_oauth import UserOauth


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

    watched_users = mongoengine.ListField(mongoengine.ReferenceField('User'))

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

    def is_watched(self, user):
        return user in self.watched_users


class Code(BaseDocument):
    user = mongoengine.ReferenceField(User)

    hash_id = mongoengine.StringField(unique=True)
    title = mongoengine.StringField()
    content = mongoengine.StringField(required=True)
    tag = mongoengine.StringField()

    def save(self, *args, **kwargs):
        self.create_hash_id(self.user.salt, 'code')
        super(Code, self).save(*args, **kwargs)

    def name(self):
        if self.title:
            return self.title
        else:
            return u'代码段: %s' % self.hash_id

    def content_head(self, n=10):
        lines = self.content.splitlines()[:n]
        return '\n'.join(lines)


class Paste(BaseDocument):
    user = mongoengine.ReferenceField(User)

    title = mongoengine.StringField()
    hash_id = mongoengine.StringField(unique=True)
    is_private = mongoengine.BooleanField(default=False)
    codes = mongoengine.ListField(mongoengine.ReferenceField(Code))
    tags = mongoengine.ListField(mongoengine.StringField())
    rate = mongoengine.IntField(default=0)
    views = mongoengine.IntField(default=0)

    likes_count = mongoengine.IntField(default=0)

    def save(self, *args, **kwargs):
        self.create_hash_id(self.user.salt, 'paste')
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

    def is_user_owned(self, user):
        return self.user == user

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created'):
            document.user.increase_counter('pastes')

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        document.user.increase_counter('pastes', -1)

signals.post_save.connect(Paste.post_save, sender=Paste)
signals.post_delete.connect(Paste.post_delete, sender=Paste)
