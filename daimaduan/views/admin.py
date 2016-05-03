from flask.ext.admin.contrib.mongoengine import ModelView
from flask_admin import Admin

from daimaduan.models.base import User
from daimaduan.models.base import Paste
from daimaduan.models.bookmark import Bookmark
from daimaduan.models.tag import Tag


admin = Admin(name="Admin", template_mode='bootstrap3')

admin.add_view(ModelView(User))
admin.add_view(ModelView(Paste))
admin.add_view(ModelView(Bookmark))
admin.add_view(ModelView(Tag))
