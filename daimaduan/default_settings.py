DEBUG = True

# Set it to 'INFO' in production
FLASK_LOG_LEVEL = 'DEBUG'

# Enable Flask-Assets debug mode.
ASSETS_DEBUG = False

# CDN
FLASK_ASSETS_USE_CDN = False
CDN_DOMAIN = 'daimaduan1.b0.upaiyun.com'
CDN_HTTPS = True
CDN_TIMESTAMP = True
ASSETS_CDN_DOMAIN = 'daimaduan1.b0.upaiyun.com'
ASSETS_CDN_HTTPS = True
ASSETS_CDN_TIMESTAMP = True


MONGODB_SETTINGS = {
    'host': '127.0.0.1',
    'db': 'daimaduan'
}

SECRET_KEY = 'Youshouldnotknowthis'

BROKER_URL = 'mongodb://127.0.0.1:27017/daimaduan_celery'

USE_JINJA_CACHE = False
MEMCACHED_URL = '127.0.0.1:11211'

EMAIL = {
    'salt': "won't tell you",
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'daimaduan',
    'password': 'guessme'
}

DOMAIN = 'daimaduan.dev:8080'

VERSION = '2.4'
DEPLOYED_AT = '2016-04-09 16:02:13'

OAUTH = {
    'github': {
        'name': 'github',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'base_url': 'https://api.github.com/',
        'callback_url': 'http://daimaduan.dev:8080/oauth/github/callback',
        'client_id': '1f8813d6e0535fbfff98',
        'client_secret': '085d8ac899e236e12feaceb528c9de63aa601d39',
        'scope': 'user:email'
    },
    'google': {
        'name': 'google',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'base_url': 'https://www.googleapis.com/oauth2/v1/',
        'callback_url': 'http://daimaduan.dev:8080/oauth/google/callback',
        'client_id': '572596272656-9urgn16qjoj36c439pecjcjmsogs76au.apps.googleusercontent.com',
        'client_secret': '085d8ac899e236e12feaceb528c9de63aa601d39',
        'scope': 'email profile openid'
    }
}
