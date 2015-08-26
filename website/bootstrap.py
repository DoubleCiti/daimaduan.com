import bottle
from bottle import request
from bottle import TEMPLATE_PATH, Jinja2Template


TEMPLATE_PATH[:] = ['templates']
Jinja2Template.settings = {
    'autoescape': True,
}
Jinja2Template.defaults = {
    'request': request
}

app = bottle.default_app()
app.config.load_config('config.cfg')

@app.hook('before_request')
def before_request():
    request.session = request.environ.get('beaker.session')


@app.hook('after_request')
def after_request():
    request.session.save()
