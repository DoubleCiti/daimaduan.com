# from beaker.middleware import SessionMiddleware

from daimaduan.bootstrap import app
from daimaduan.bootstrap import app_root
import daimaduan.views


# session_opts = {
#     'session.type': 'file',
#     'session.cookie_expires': 7 * 24 * 3600,
#     'session.data_dir': '/tmp/sessions',
#     'session.auto': True
# }
# application = SessionMiddleware(app, session_opts)
application = app
