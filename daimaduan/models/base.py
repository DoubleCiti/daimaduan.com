# coding: utf-8
import hashlib
import time

from mongoengine import signals
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from daimaduan.bootstrap import db
from daimaduan.models import BaseDocument
from daimaduan.models.user_oauth import UserOauth


class User(BaseDocument):
    username = db.StringField(required=True)
    email = db.StringField(required=True)
    password = db.StringField()
    salt = db.StringField()
    is_email_confirmed = db.BooleanField(default=False)
    email_confirmed_on = db.DateTimeField(default=None)

    oauths = db.ListField(db.ReferenceField('UserOauth'))

    likes = db.ListField(db.ReferenceField('Paste'))
    followers = db.ListField(db.ReferenceField('User'))

    @property
    def pastes(self):
        return Paste.objects(user=self)

    @property
    def pastes_count(self):
        return len(self.pastes)

    @property
    def private_pastes_count(self):
        return len(self.pastes(is_private=True))

    @property
    def public_pastes_count(self):
        return len(self.pastes) - len(self.pastes(is_private=True))

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

    def is_followed(self, user):
        return user in self.followers


class Code(db.EmbeddedDocument):
    title = db.StringField()
    content = db.StringField(required=True)
    syntax = db.StringField()

    def content_head(self, n=10):
        lines = self.content.splitlines()[:n]
        return '\n'.join(lines)

    @property
    def highlight_content(self):
        lexer = get_lexer_by_name(self.tag, stripall=True)
        formatter = HtmlFormatter(linenos=True, cssclass='codehilite')
        return highlight(self.content, lexer, formatter)


class Paste(BaseDocument):
    user = db.ReferenceField(User)

    title = db.StringField()
    hash_id = db.StringField(unique=True)
    is_private = db.BooleanField(default=False)
    codes = db.ListField(db.EmbeddedDocumentField(Code))
    tags = db.ListField(db.StringField())

    views = db.IntField(default=0)

    def save(self, *args, **kwargs):
        self.create_hash_id(self.user.salt, 'paste')
        if not self.title:
            self.title = u'代码集合: %s' % self.hash_id
        super(Paste, self).save(*args, **kwargs)

    def increase_views(self):
        self.views = self.views + 1
        self.save()

    @property
    def disqus_identifier(self):
        return 'paste-%s' % self.hash_id

    def is_user_owned(self, user):
        return self.user == user

    @property
    def likes_count(self):
        return User.objects(likes=self).count()
