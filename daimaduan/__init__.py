from daimaduan.bootstrap import app

import daimaduan.views
from beaker.middleware import SessionMiddleware

session_opts = {
    'session.type': 'cookie',
    'session.cookie_expires': 7 * 24 * 3600,
    'session.auto': True,
    'session.validate_key': app.config['site.validate_key']
}
application = SessionMiddleware(app, session_opts)
