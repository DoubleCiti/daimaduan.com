# coding: utf-8
from bottle import abort
from bottle import request
from bottle import redirect
from bottle import jinja2_view

from bottle_utils.csrf import csrf_protect
from bottle_utils.csrf import csrf_token

from daimaduan.bootstrap import app
from daimaduan.bootstrap import login

from daimaduan.forms import PasteForm

from daimaduan.models import Code
from daimaduan.models import Paste
from daimaduan.models import Rate
from daimaduan.models import Tag
from daimaduan.models import Syntax
from daimaduan.utils import jsontify
from daimaduan.utils import user_active_required


ITEMS_PER_PAGE = 20


@app.route('/', name='pastes.index')
@jinja2_view('index.html')
def index():
    return {'pastes': Paste.objects(is_private=False).order_by('-updated_at')[:ITEMS_PER_PAGE],
            'tags': Syntax.objects(),
            'has_more_pastes': Paste.objects(is_private=False).count() > ITEMS_PER_PAGE}


@app.route('/pastes/more', name="pastes.more")
@jinja2_view('pastes/pastes.html')
def pastes_more():
    p = int(request.query.p)
    if not p:
        return {}
    return {'pastes': Paste.objects(is_private=False).order_by('-updated_at')[(p - 1) * ITEMS_PER_PAGE:p * ITEMS_PER_PAGE]}


@app.get('/create', name='pastes.create')
@login.login_required
@user_active_required
@jinja2_view('pastes/create.html')
@csrf_token
def create_get():
    form = PasteForm(data={'codes': [{'title': '', 'content': ''}]})
    return {'form': form, 'token': request.csrf_token}


@app.post('/create', name='pastes.create')
@login.login_required
@user_active_required
@jinja2_view('pastes/create.html')
@csrf_token
@csrf_protect
def create_post():
    form = PasteForm(request.POST)
    if form.validate():
        user = login.get_user()
        paste = Paste(title=form.title.data, user=user, is_private=form.is_private.data)
        tags = []
        for i, c in enumerate(form.codes):
            tag_name = c.tag.data.lower()
            if not c.title.data:
                c.title.data = '代码片段%s' % (i + 1)
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
        return redirect('/paste/%s' % paste.hash_id)
    return {'form': form, 'token': request.csrf_token}


@app.route('/paste/<hash_id>', name='pastes.show')
@jinja2_view('pastes/view.html')
def view(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    paste.views += 1
    paste.save()
    return {'paste': paste}


@app.route('/paste/<hash_id>/edit', name='pastes.update')
@login.login_required
@jinja2_view('pastes/edit.html')
@csrf_token
def edit_get(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    if paste.user.id != request.user.id:
        abort(404)
    data = {'title': paste.title,
            'is_private': paste.is_private,
            'codes': [{'title': code.title, 'content': code.content, 'tag': code.tag} for code in paste.codes]}
    form = PasteForm(data=data)
    return {'form': form, 'paste': paste, 'token': request.csrf_token}


@app.post('/paste/<hash_id>/edit', name='pastes.update')
@login.login_required
@jinja2_view('pastes/edit.html')
@csrf_token
@csrf_protect
def edit_post(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    if paste.user.id != request.user.id:
        abort(404)
    form = PasteForm(request.POST)
    if form.validate():
        user = login.get_user()
        paste.title = form.title.data
        paste.is_private = form.is_private.data
        tags = []
        codes = [code for code in paste.codes]
        paste.codes = []
        for code in codes:
            code.delete()
        for i, c in enumerate(form.codes):
            tag_name = c.tag.data.lower()
            if not c.title.data:
                c.title.data = '代码片段%s' % (i + 1)
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
        return redirect('/paste/%s' % paste.hash_id)
    return {'form': form, 'paste': paste, 'token': request.csrf_token}


@app.get('/paste/<hash_id>/delete', name='pastes.delete')
@login.login_required
def delete(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    if paste.user.id != request.user.id:
        abort(404)
    paste.delete()
    return redirect('/')


@app.route('/tags', name='tags.index')
@jinja2_view('tags/index.html')
def tags():
    return {'tags': Tag.objects().order_by('-popularity')}


@app.route('/tag/<tag_name>', name='tags.show')
@jinja2_view('tags/view.html')
def tag(tag_name):
    return {'tag': Syntax.objects(name=tag_name).first(),
            'pastes': Paste.objects(tags=tag_name, is_private=False).order_by('-updated_at')[:ITEMS_PER_PAGE]}


@app.route('/tag/<tag_name>/more')
@jinja2_view('pastes/pastes.html')
def tag_more(tag_name):
    p = int(request.query.p)
    if not p:
        return {}
    return {'pastes': Paste.objects(tags=tag_name, is_private=False).order_by('-updated_at')[(p - 1) * ITEMS_PER_PAGE:p * ITEMS_PER_PAGE]}


@app.route('/favourite/<hash_id>', name='favourites.add')
def favourites_add(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    if paste not in request.user.favourites:
        request.user.favourites.append(paste)
        request.user.save()
    redirect('/paste/%s' % hash_id)


@app.route('/unfavourite/<hash_id>', name='favourites.remove')
def favourites_remove(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    if paste in request.user.favourites:
        request.user.favourites.remove(paste)
        request.user.save()
    redirect('/paste/%s' % hash_id)
