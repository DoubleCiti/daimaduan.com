#-*-encoding:utf-8-*-
from bootstrap import app
from bottle import run, request, redirect
from bottle import jinja2_view
from bottle import static_file

from beaker.middleware import SessionMiddleware

from models import PasteForm
from models import User
from models import Paste

from forms import SignupForm
from forms import SigninForm

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
@jinja2_view('signup.html')
def signup_post():
    form = SignupForm(request.forms)
    if form.validate():
        user = User()
        form.populate_obj(user)
        user.save()

        return redirect('/signin')
    
    return { 'form': form }

# FIXME: 将注销改为 DELETE 请求
@app.get('/signin')
@jinja2_view('signin.html')
def signin_get():
    return {'form': SigninForm()}


@app.post('/signin')
@jinja2_view('signin.html')
def signin_post():
    form = SigninForm(request.POST)
    if form.validate():
        request.session['username'] = form.user.username
        redirect('/')
    else:
        return locals();


@app.delete('/signout')
def signout_delete():
    del request.session['username']

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
