#-*-encoding:utf-8-*-
import datetime
import time
import hashlib
import wtforms
import mongoengine

from bootstrap import app

mongoengine.connect(app.config['mongodb.database'], host=app.config['mongodb.host'])


class SigninForm(wtforms.Form):
    email = wtforms.StringField(u'email')
    password = wtforms.PasswordField(u'password')


class PasteForm(wtforms.Form):
    title = wtforms.StringField(u'title')
    content = wtforms.TextAreaField(u'content')


class BaseDocument(mongoengine.Document):
    meta = { 'abstract': True }

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


class Paste(BaseDocument):
    user = mongoengine.ReferenceField(User)

    hash_id = mongoengine.StringField()
    title = mongoengine.StringField()
    content = mongoengine.StringField(required=True)

    def save(self, *args, **kwargs):
        # TODO: needs to make sure hash_id is unique
        self.hash_id = hashlib.sha1('%s%s' % (self.user.salt, str(time.time()))).hexdigest()[:10]
        super(Paste, self).save(*args, **kwargs)
