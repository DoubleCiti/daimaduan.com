# coding: utf-8
import datetime

from daimaduan.bootstrap import db


NEW_PASTE = u"您关注的用户 [{user_username}]({user_url}) 发布了新的代码集合 [{paste_title}]({paste_url})"
NEW_COMMENT = u"用户 [{user_username}]({user_url}) 评论了您的代码集合 [{paste_title}]({paste_url})"
WATCH = u"用户 [{user_username}]({user_url}) 关注了您"
BOOKMARK = u"用户 [{user_username}]({user_url}) 收藏了您的代码集合 [{paste_title}]({paste_url}) 到收藏夹 [{bookmark_title}]({bookmark_url})"
LIKE = u"用户 [{user_username}]({user_url}) 喜欢了您的代码集合 [{paste_title}]({paste_url})"


class Message(db.Document):
    user = db.ReferenceField('User')
    who = db.ReferenceField('User')
    content = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
