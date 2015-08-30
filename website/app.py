# coding: utf-8
from bootstrap import app, login
from bottle import run, request, redirect, abort
from bottle import error
from bottle import jinja2_view
from bottle import static_file

from beaker.middleware import SessionMiddleware

from models import User
from models import Code
from models import Paste

from forms import SignupForm
from forms import SigninForm


@error(404)
@jinja2_view('error.html')
def error_404(error):
    return {'title': u"页面找不到", 'message': u"您所访问的页面不存在!"}


@error(500)
@jinja2_view('error.html')
def error_500(error):
    return {'title': u"服务器错误", 'message': u"服务器开小差了, 晚点再来吧!"}


@login.load_user
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.route('/')
@jinja2_view('index.html')
def index():
    return {'pastes': Paste.objects()}


@app.get('/create')
@jinja2_view('create.html')
def create_get():
    return {}


@app.post('/create')
@jinja2_view('create.html')
def create():
    title_list = request.forms.getlist('title')
    content_list = request.forms.getlist('content')
    if len(title_list) != len(content_list):
        return {}
    user = User.objects(username=request.session['username']).first()
    paste = Paste(user=user, title=request.forms.get('paste_title', None))
    for i in range(len(title_list)):
        code = Code(title=title_list[i],
                    content=content_list[i],
                    user=user)
        code.save()
        paste.codes.append(code)
    paste.save()
    return redirect('/')


@app.route('/paste/<hash_id>')
@jinja2_view('view.html')
def view(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    return {'paste': paste}


@app.get('/signup')
@jinja2_view('signup.html')
def signup_get():
    return {'form': SignupForm()}


@app.post('/signup')
@jinja2_view('signup.html')
def signup_post():
    form = SignupForm(request.forms)
    if form.validate():
        user = User()
        form.populate_obj(user)
        user.save()
        return redirect('/signin')

    return { 'form': form }


@app.get('/signin')
@jinja2_view('signin.html')
def signin_get():
    return {'form': SigninForm()}


@app.post('/signin')
@jinja2_view('signin.html')
def signin_post():
    form = SigninForm(request.POST)
    if form.validate():
        login.login_user(str(form.user.id))
        redirect('/')
    else:
        return locals();


@app.delete('/signout')
def signout_delete():
    login.logout_user()
    request.environ.get('beaker.session').delete()


session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 7 * 24 * 3600,
    'session.data_dir': './sessions',
    'session.auto': True
}
application = SessionMiddleware(app, session_opts)


if __name__ == '__main__':
    @app.route('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root='./static')

    run(application, host='0.0.0.0', server='paste', port=8080, reloader=True, debug=True)
