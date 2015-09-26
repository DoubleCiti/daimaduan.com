# coding: utf-8
from bootstrap import app, login
from bottle import run, request, redirect, abort
from bottle import jinja2_view
from bottle import static_file

from beaker.middleware import SessionMiddleware
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

from models import User
from models import Code
from models import Paste
from models import Tag

from forms import SignupForm
from forms import SigninForm
from forms import PasteForm


@login.load_user
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.route('/')
@jinja2_view('index.html')
def index():
    return {'pastes': Paste.objects().order_by('-updated_at')}


@app.get('/create')
@login.login_required
@jinja2_view('pastes/create.html')
def create_get():
    form = PasteForm(data={'codes': [{'title': '', 'content': ''}]})
    return {'form': form}


@app.post('/create')
@login.login_required
@jinja2_view('pastes/create.html')
def create_post():
    form = PasteForm(request.POST)
    if form.validate():
        user = login.get_user()
        paste = Paste(title=form.title.data, user=user)
        tags = []
        for c in form.codes:
            try:
                lexer = guess_lexer(c.content.data)
                tag_name = lexer.name.lower()
            except ClassNotFound:
                tag_name = 'text'
            code = Code(title=c.title.data,
                        content=c.content.data,
                        tag=tag_name,
                        user=user)
            code.save()
            tags.append(tag_name)
            tag = Tag.objects(name=tag_name).first()
            if tag:
                tag.popularity += 1
            else:
                tag = Tag(name=tag_name)
            tag.save()
            paste.codes.append(code)
        paste.tags = list(set(tags))
        paste.save()
        return redirect('/')
    else:
        return {'form': form}



@app.route('/paste/<hash_id>')
@jinja2_view('pastes/view.html')
def view(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    return {'paste': paste}


@app.route('/tags')
@jinja2_view('tags/index.html')
def tags():
    return {'tags': Tag.objects().order_by('-popularity')}


@app.route('/tag/<tag_name>')
@jinja2_view('tags/view.html')
def tag(tag_name):
    return {'tag': Tag.objects(name=tag_name).first(),
            'pastes': Paste.objects(tags=tag_name)[:10]}


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

    run(application, host='0.0.0.0',
                     server='paste',
                     port=8080,
                     reloader=True,
                     debug=True)
