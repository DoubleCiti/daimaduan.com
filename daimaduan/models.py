# coding: utf-8
import datetime
import time
import hashlib
import mongoengine

from bottle import request

from daimaduan.jinja_ext import time_passed


class BaseDocument(mongoengine.Document):
    meta = {'abstract': True, 'strict': False}

    created_at = mongoengine.DateTimeField(default=datetime.datetime.now)
    updated_at = mongoengine.DateTimeField(default=datetime.datetime.now)


class User(BaseDocument):
    username = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    salt = mongoengine.StringField()
    favourites = mongoengine.ListField(mongoengine.ReferenceField("Paste"))

    oauths = mongoengine.ListField(mongoengine.ReferenceField('UserOauth'))

    def save(self, *args, **kwargs):
        if not self.salt:
            self.salt = hashlib.sha1(str(time.time())).hexdigest()
            self.password = self.generate_password(self.password)
        super(User, self).save(*args, **kwargs)

    def generate_password(self, string):
        return hashlib.sha1('%s%s' % (string, self.salt)).hexdigest()

    def check_login(self, password):
        return self.generate_password(password) == self.password

    def gravatar_url(self, width=80):
        return "http://cn.gravatar.com/avatar/%s?s=%d" % (hashlib.md5(self.email).hexdigest(), width)

    @classmethod
    def find_by_oauth(cls, provider, openid):
        """Find user that has oauth info with given provider and openid"""

        oauth = UserOauth.objects(provider=provider, openid=openid).first()

        if oauth and oauth.user:
            return oauth.user

    def get_favourites_by_page(self, p):
        return self.favourites[(p - 1) * 20:p * 20]

    def is_in_favourites(self, paste):
        return paste in self.favourites

    def to_json(self):
        return {'username': self.username,
                'gravatar_url': self.gravatar_url(width=38)}


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

    def to_json(self):
        return {'hash_id': self.hash_id,
                'title': self.title,
                'tags': self.tags,
                'num_codes': len(self.codes),
                'time_passed': time_passed(self.updated_at),
                'user': self.user.to_json()}

    def is_user_favourited(self):
        if request.user:
            return request.user.is_in_favourites(self)
        return False

    def to_disqus_identifier(self):
        return 'paste-%s' % self.hash_id



class Tag(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)
    popularity = mongoengine.IntField(default=1)


class Syntax(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)


class Rate(BaseDocument):
    user = mongoengine.ReferenceField(User)
    paste = mongoengine.ReferenceField(Paste)
    score = mongoengine.IntField(default=0)
