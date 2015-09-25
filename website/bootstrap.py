# coding: utf-8
import bottle
from bottle import request
from bottle import TEMPLATE_PATH, Jinja2Template
from bottle import error
from bottle import jinja2_view
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


@error(404)
@jinja2_view('error.html')
def error_404(error):
    return {'title': u"页面找不到", 'message': u"您所访问的页面不存在!"}


@error(500)
@jinja2_view('error.html')
def error_500(error):
    return {'title': u"服务器错误", 'message': u"服务器开小差了, 晚点再来吧!"}


@error(401)
@jinja2_view('error.html')
def error_401(error):
    return {'title': u'请登录', 'message': u'请登录后再执行此操作!'}
