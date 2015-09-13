import bottle
from bottle import request
from bottle import TEMPLATE_PATH, Jinja2Template
from bottle_login import LoginPlugin


TEMPLATE_PATH[:] = ['templates']
Jinja2Template.settings = {
    'autoescape': True,
}
Jinja2Template.defaults = {
    'request': request
}

app = bottle.default_app()
app.config.load_config('config.cfg')
app.config['SECRET_KEY'] = app.config['site.secret_key']
login = app.install(LoginPlugin())

@app.hook('before_request')
def before_request():
    # this line is used for bottle-login plugin
    request.environ['session'] = request.environ.get('beaker.session')
    request.user = login.get_user()


@app.hook('after_request')
def after_request():
    # update beaker.session and then save it
    request.environ.get('beaker.session').update(request.environ['session'])
    request.environ.get('beaker.session').save()
