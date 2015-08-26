#-*-encoding:utf-8-*-
from bootstrap import app
from bottle import run, request, redirect
from bottle import jinja2_view, TEMPLATE_PATH, Jinja2Template
from bottle import static_file

from beaker.middleware import SessionMiddleware

from models import SigninForm
from models import SignupForm
from models import PasteForm
from models import User
from models import Paste


TEMPLATE_PATH[:] = ['templates']
Jinja2Template.settings = {
    'autoescape': True,
}
Jinja2Template.defaults = {
    'request': request
}


@app.hook('before_request')
def before_request():
    request.session = request.environ.get('beaker.session')


@app.hook('after_request')
def after_request():
    request.session.save()


@app.route('/')
@jinja2_view('index.html')
def index():
    return {'pastes': Paste.objects()}


@app.get('/create')
@jinja2_view('create.html')
def create_get():
    return {'form': PasteForm()}


@app.post('/create')
def create():
    form = PasteForm(request.POST)
    if form.validate():
        user = User.objects(username=request.session['username']).first()
        paste = Paste(title=form.title.data,
                      content=form.content.data,
                      user=user)
        paste.save()
    return redirect('/')


@app.route('/paste/<hash_id>')
@jinja2_view('view.html')
def view(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    return {'paste': paste}

@app.get('/signup')
@jinja2_view('signup.html')
def signup_get():
    return {'form': SignupForm()}


@app.post('/signup')
def signup_post():
    form = SignupForm(request.POST)
    if form.validate():
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data
        user.save()

        return redirect('/signin')


# FIXME: 将注销改为 DELETE 请求
@app.get('/signin')
@jinja2_view('signin.html')
def signin_get():
    return {'form': SigninForm()}


@app.post('/signin')
def signin_post():
    form = SignupForm(request.POST)
    user = User.objects(email=form.email.data).first()
    if user.generate_password(form.password.data) == user.password:
        request.session['username'] = user.username
        redirect('/')

@app.get('/signout')
def signout_get():
    del request.session['username']
    redirect('/')

@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 7 * 24 * 3600,
    'session.data_dir': './sessions',
    'session.auto': True
}
app = SessionMiddleware(app, session_opts)
run(app, server='paste', port=8080, reloader=True, debug=True)
