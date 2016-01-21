# coding: utf-8
import base64
import hashlib
import hmac
import json
import time

from flask import abort, jsonify, url_for
from flask import current_app, request
from flask import make_response
from flask import redirect
from flask import render_template, Blueprint
from flask_login import current_user
from flask_login import login_required

from daimaduan.forms.paste import PasteForm
from daimaduan.models.base import Paste, Code, User
from daimaduan.models.message import Message
from daimaduan.models.message_category import NEW_PASTE
from daimaduan.models.syntax import Syntax
from daimaduan.models.tag import Tag
from daimaduan.utils.decorators import user_active_required


paste_app = Blueprint("paste_app", __name__, template_folder="templates")


def create_message(user, paste):
    user.messages.append(Message(category=NEW_PASTE,
                                 content=u"您关注的用户 [%s](%s) 发表了新的代码集合 [%s](%s)" % (
                                     paste.user.username,
                                     url_for('user_app.view_user', username=paste.user.username),
                                     paste.title,
                                     url_for('paste_app.view_paste', hash_id=paste.hash_id))))
    user.save()


@paste_app.route('/create', methods=['GET', 'POST'])
@login_required
@user_active_required
def create_paste():
    if request.method == 'GET':
        # missing csrf
        return render_template('pastes/create.html',
                               form=PasteForm(data={'codes': [{'title': '', 'content': ''}]}))
    else:
        form = PasteForm(request.form)
        if form.validate():
            user = current_user.user
            paste = Paste(title=form.title.data, user=user, is_private=form.is_private.data)
            # tags = []
            for i, c in enumerate(form.codes):
                syntax = Syntax.objects(key=c.syntax.data).get_or_404()
                if not c.title.data:
                    c.title.data = '代码片段%s' % (i + 1)
                code = Code(title=c.title.data,
                            content=c.content.data,
                            syntax=syntax)
                # tags.append(syntax)
                # tag = Tag.objects(name=syntax).first()
                # if tag:
                #     tag.popularity += 1
                # else:
                #     tag = Tag(name=syntax)
                # tag.save()
                paste.codes.append(code)
            # paste.tags = list(set(tags))
            paste.save()
            followers = User.objects(followers=user)
            for follower in followers:
                create_message(follower, paste)
            return redirect('/paste/%s' % paste.hash_id)
        return render_template('pastes/create.html',
                               form=form)


@paste_app.route('/<hash_id>', methods=['GET'])
def view_paste(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)
    paste.increase_views()

    sig = message = timestamp = None
    if current_user.is_authenticated:
        # create a JSON packet of our data attributes
        data = json.dumps({'id': str(current_user.id),
                           'username': current_user.username,
                           'email': current_user.email,
                           'avatar': current_user.user.gravatar_url()})
        # encode the data to base64
        message = base64.b64encode(data)
        # generate a timestamp for signing the message
        timestamp = int(time.time())
        # generate our hmac signature
        sig = hmac.HMAC(current_app.config['DISQUS']['secret_key'], '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()

    return render_template('pastes/view.html',
                           paste=paste,
                           message=message,
                           timestamp=timestamp,
                           sig=sig)


@paste_app.route('/<hash_id>/edit', methods=['GET', 'POST'])
@login_required
@user_active_required
def edit_paste(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)
    if not paste.is_user_owned(current_user.user):
        abort(404)
    if request.method == 'GET':
        data = {'title': paste.title,
                'is_private': paste.is_private,
                'codes': [{'title': code.title, 'content': code.content, 'syntax': code.syntax.key} for code in paste.codes]}
        form = PasteForm(data=data)
        return render_template('pastes/edit.html',
                               form=form,
                               paste=paste)
    else:
        form = PasteForm(request.form)
        if form.validate():
            paste.title = form.title.data
            paste.is_private = form.is_private.data
            paste.codes = []
            # tags = []
            for i, c in enumerate(form.codes):
                syntax = Syntax.objects(key=c.syntax.data).get_or_404()
                if not c.title.data:
                    c.title.data = '代码片段%s' % (i + 1)
                code = Code(title=c.title.data,
                            content=c.content.data,
                            syntax=syntax)
                # tags.append(syntax)
                # tag = Tag.objects(name=syntax).first()
                # if tag:
                #     tag.popularity += 1
                # else:
                #     tag = Tag(name=syntax)
                # tag.save()
                paste.codes.append(code)
            # paste.tags = list(set(tags))
            paste.save()
            return redirect('/paste/%s' % paste.hash_id)
        return render_template('pastes/edit.html',
                               form=form,
                               paste=paste)


@paste_app.route('/<hash_id>/like', methods=['POST'])
@login_required
def like(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)
    user = current_user.user
    is_user_liked = paste in user.likes
    if not is_user_liked:
        user.likes.append(paste)
        user.save()
    return jsonify(dict(paste_id=hash_id,
                        user_like=len(user.likes),
                        paste_likes=len(user.likes),
                        liked=True))


@paste_app.route('/<hash_id>/unlike', methods=['POST'])
@login_required
def unlike(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)
    user = current_user.user
    is_user_liked = paste in user.likes
    if is_user_liked:
        user.likes.remove(paste)
        user.save()
    return jsonify(dict(paste_id=hash_id,
                        user_like=len(user.likes),
                        paste_likes=len(user.likes),
                        liked=True))


@paste_app.route('/<hash_id>/delete', methods=['POST'])
@login_required
def delete(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)

    if current_user.user.owns_record(paste):
        paste.delete()
        return redirect('/')
    else:
        abort(403)


@paste_app.route('/<hash_id>/embed.js', methods=['GET'])
def embed_js(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)

    resp = make_response(render_template('pastes/embed.js', paste=paste), 200)
    resp.headers['Content-Type'] = 'text/javascript; charset=utf-8'
    return resp
