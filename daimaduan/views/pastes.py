# coding: utf-8
from bottle import abort
from bottle import request
from bottle import redirect
from bottle import jinja2_view

from daimaduan.bootstrap import app
from daimaduan.bootstrap import login

from daimaduan.forms import PasteForm

from daimaduan.models import Code
from daimaduan.models import Paste
from daimaduan.models import Rate
from daimaduan.models import Tag
from daimaduan.utils import jsontify


@app.route('/', name='pastes.index')
@jinja2_view('index.html')
def index():
    return {'pastes': Paste.objects(is_private=False).order_by('-updated_at')[:20],
            'tags': Tag.objects().order_by('-popularity')[:10]}


@app.route('/pastes/more', name="pastes.more")
@jsontify
def pastes_more():
    p = int(request.query.p)
    if not p:
        return {}
    pastes_objects = Paste.objects(is_private=False).order_by('-updated_at')[(p - 1) * 20:p * 20]
    return {'pastes': [paste.to_json() for paste in pastes_objects]}


@app.get('/create', name='pastes.create')
@login.login_required
@jinja2_view('pastes/create.html')
def create_get():
    form = PasteForm(data={'codes': [{'title': '', 'content': ''}]})
    return {'form': form}


@app.post('/create', name='pastes.create')
@login.login_required
@jinja2_view('pastes/create.html')
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
    return {'form': form}


@app.route('/paste/<hash_id>', name='pastes.show')
@jinja2_view('pastes/view.html')
def view(hash_id):
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    return {'paste': paste}


@app.route('/paste/<hash_id>/edit', name='pastes.update')
@login.login_required
@jinja2_view('pastes/edit.html')
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
    return {'form': form, 'paste': paste}


@app.post('/paste/<hash_id>/edit', name='pastes.update')
@login.login_required
@jinja2_view('pastes/edit.html')
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
        for code in paste.codes:
            paste.codes.remove(code)
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
    return {'form': form, 'paste': paste}


@app.post('/rate/<hash_id>', name='rate.post')
@login.login_required
@jsontify
def rate_post(hash_id):
    score = request.forms.get('score', None)
    if not score:
        abort(404)
    paste = Paste.objects(hash_id=hash_id).first()
    if not paste:
        abort(404)
    user = login.get_user()
    rate = Rate.objects(paste=paste, user=user).first()
    if not rate:
        rate = Rate(paste=paste, user=user, score=request.forms.get('score', score))
        rate.save()
    rates = 0
    rate_objects = Rate.objects(paste=paste)
    for t in rate_objects:
        rates += t.score
    paste.rate = int(rates / len(rate_objects))
    paste.save()
    return {'status': 'ok'}


@app.route('/tags', name='tags.index')
@jinja2_view('tags/index.html')
def tags():
    return {'tags': Tag.objects().order_by('-popularity')}


@app.route('/tag/<tag_name>', name='tags.show')
@jinja2_view('tags/view.html')
def tag(tag_name):
    return {'tag': Tag.objects(name=tag_name).first(),
            'pastes': Paste.objects(tags=tag_name)[:10]}


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
