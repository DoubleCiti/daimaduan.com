# coding: utf-8
from bottle import error
from bottle import jinja2_view


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


@error(403)
@jinja2_view('error.html')
def error_403(error):
    return {'title': u'请激活email', 'message': u'请激活您在代码段注册的邮箱地址再进行操作!'}
