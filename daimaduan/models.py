# coding: utf-8
import datetime
import time
import hashlib
import mongoengine

from daimaduan.bootstrap import app

mongoengine.connect(app.config['mongodb.database'], host=app.config['mongodb.host'])


class BaseDocument(mongoengine.Document):
    meta = { 'abstract': True, 'strict': False }

    created_at = mongoengine.DateTimeField(default=datetime.datetime.now)
    updated_at = mongoengine.DateTimeField(default=datetime.datetime.now)


class User(BaseDocument):
    username = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    salt= mongoengine.StringField()

    def save(self, *args, **kwargs):
        if not self.salt:
            self.salt = hashlib.sha1(str(time.time())).hexdigest()
            self.password = self.generate_password(self.password)
        super(User, self).save(*args, **kwargs)

    def generate_password(self, string):
        return hashlib.sha1('%s%s' % (string, self.salt)).hexdigest()

    def check_login(self, password):
        return self.generate_password(password) == self.password

    def gravatar_url(self):
        return "http://gravatar.duoshuo.com/avatar/%s" % hashlib.md5(self.email).hexdigest()


class Code(BaseDocument):
    user = mongoengine.ReferenceField(User)

    hash_id = mongoengine.StringField()
    title = mongoengine.StringField()
    content = mongoengine.StringField(required=True)
    tag = mongoengine.StringField()

    def save(self, *args, **kwargs):
        # TODO: needs to make sure hash_id is unique
        self.hash_id = hashlib.sha1('%s%s' % (self.user.salt, str(time.time()))).hexdigest()[:10]
        if not self.title:
            self.title = u'代码片段: %s' % self.hash_id
        super(Code, self).save(*args, **kwargs)

    def name(self):
        if len(self.title):
            return self.title
        else:
            return u'代码段: %s' % self.hash_id


class Paste(BaseDocument):
    user = mongoengine.ReferenceField(User)

    title = mongoengine.StringField()
    hash_id = mongoengine.StringField()
    codes = mongoengine.ListField(mongoengine.ReferenceField(Code))
    tags = mongoengine.ListField(mongoengine.StringField())

    def save(self, *args, **kwargs):
        # TODO: needs to make sure hash_id is unique
        self.hash_id = hashlib.sha1('%s%s' % (self.user.salt, str(time.time()))).hexdigest()[:10]
        if not self.title:
            self.title = u'代码集合: %s' % self.hash_id
        super(Paste, self).save(*args, **kwargs)


class Tag(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)
    popularity = mongoengine.IntField(default=1)


class Syntax(BaseDocument):
    name = mongoengine.StringField(required=True, unique=True)
