# coding: utf-8
import time

from flask import g
from flask import render_template

from daimaduan.bootstrap import app


@app.before_request
def before_request():
    g.started_at = time.time()


@app.errorhandler(401)
def error_401(error):
    return render_template('error.html',
                           title=u'请登录',
                           message=u'请登录后再执行此操作!')


@app.errorhandler(404)
def error_404(error):
    return render_template('error.html',
                           title=u"页面找不到",
                           message=u"您所访问的页面不存在!")


@app.errorhandler(500)
def error_500(error):
    if hasattr(error, 'description'):
        message = error.description
    else:
        message = u"服务器开小差了, 晚点再来吧!"
    return render_template('error.html',
                           title=u"服务器错误",
                           message=message)
