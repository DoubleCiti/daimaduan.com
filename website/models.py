# coding: utf-8
import datetime
import time
import hashlib
import wtforms
import mongoengine

from bootstrap import app

mongoengine.connect(app.config['mongodb.database'], host=app.config['mongodb.host'])


class BaseDocument(mongoengine.Document):
    meta = { 'abstract': True }

    created_at = mongoengine.DateTimeField(default=datetime.datetime.now)
    updated_at = mongoengine.DateTimeField(default=datetime.datetime.now)


class User(BaseDocument):
    username = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    salt = mongoengine.StringField()
    email_confirm_code = mongoengine.StringField()
    is_email_confirmed = mongoengine.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.salt:
            self.salt = hashlib.sha1(str(time.time())).hexdigest()
            self.password = self.generate_password(self.password)
        if not self.email_confirm_code:
            self.email_confirm_code = hashlib.sha1("%s%s" % (self.username, self.salt)).hexdigest()
        super(User, self).save(*args, **kwargs)

    def generate_password(self, string):
        return hashlib.sha1('%s%s' % (string, self.salt)).hexdigest()

    def check_login(self, password):
        return self.generate_password(password) == self.password


class Code(BaseDocument):
    user = mongoengine.ReferenceField(User)

    hash_id = mongoengine.StringField()
    title = mongoengine.StringField()
    content = mongoengine.StringField(required=True)

    def save(self, *args, **kwargs):
        # TODO: needs to make sure hash_id is unique
        self.hash_id = hashlib.sha1('%s%s' % (self.user.salt, str(time.time()))).hexdigest()[:10]

    def name(self):
        if len(self.title):
            return self.title
        else:
            return u'代码段: %s' % self.hash_id
        super(Code, self).save(*args, **kwargs)


class Paste(BaseDocument):
    user = mongoengine.ReferenceField(User)

    title = mongoengine.StringField()
    hash_id = mongoengine.StringField()
    codes = mongoengine.ListField(mongoengine.ReferenceField(Code))

    def save(self, *args, **kwargs):
        # TODO: needs to make sure hash_id is unique
        self.hash_id = hashlib.sha1('%s%s' % (self.user.salt, str(time.time()))).hexdigest()[:10]
        super(Paste, self).save(*args, **kwargs)
