# coding: utf-8
from flask import abort
from flask import flash
from flask import jsonify
from flask import url_for
from flask import current_app
from flask import request
from flask import make_response
from flask import redirect
from flask import render_template, Blueprint
from flask_login import current_user
from flask_login import login_required

from daimaduan.forms.paste import PasteForm
from daimaduan.forms.paste import CommentForm
from daimaduan.models.base import Paste
from daimaduan.models.base import Code
from daimaduan.models.base import User
from daimaduan.models.base import Comment
from daimaduan.models.message import NEW_PASTE
from daimaduan.models.message import NEW_COMMENT
from daimaduan.models.message import LIKE
from daimaduan.models.message import Message
from daimaduan.models.bookmark import Bookmark
from daimaduan.models.syntax import Syntax
from daimaduan.models.tag import Tag
from daimaduan.utils.decorators import user_active_required
from daimaduan.utils import logger


paste_app = Blueprint("paste_app", __name__, template_folder="templates")


def save_paste_and_codes(form, paste=None):
    if not paste:
        paste = Paste(user=current_user.user)

    paste.title = form.title.data
    paste.is_private = form.is_private.data
    paste.codes = []
    tags = form.tags.data.split(',')

    for i, c in enumerate(form.codes):
        syntax = Syntax.objects(key=c.syntax.data).get_or_404()
        if not c.title.data:
            c.title.data = '代码片段%s' % (i + 1)
        code = Code(title=c.title.data,
                    content=c.content.data,
                    syntax=syntax)
        paste.codes.append(code)

    for key in tags:
        syntax = Syntax.objects(name__iexact=key).first()
        tag = Tag.objects(key__iexact=key).first()
        if not tag and syntax:
            tag = Tag(key=syntax.key, name=syntax.name, is_default_tag=True)
        elif not tag and not syntax:
            tag = Tag(key=key, name=key)
        else:
            tag.popularity += 1
        tag.save()
        if tag not in paste.tags:
            paste.tags.append(tag)
    paste.save()
    return paste


@paste_app.route('/create', methods=['GET', 'POST'])
@login_required
@user_active_required
def create_paste():
    if request.method == 'GET':
        # missing csrf
        form = PasteForm(data={'codes': [{'title': '', 'content': ''}]})
        return render_template('pastes/create.html', form=form)
    else:
        form = PasteForm(request.form)
        if form.validate():
            user = current_user.user
            paste = save_paste_and_codes(form)
            if not paste.is_private:
                followers = User.objects(followings=user)
                content = NEW_PASTE.format(user_username=user.username,
                                           user_url=url_for('user_app.view', username=user.username),
                                           paste_title=paste.title,
                                           paste_url=url_for('paste_app.view_paste', hash_id=paste.hash_id))
                for follower in followers:
                    message = Message(user=follower,
                                      who=user,
                                      content=content)
                    message.save()
            return jsonify(success=True, hash_id=paste.hash_id)
        else:
            errors = form.errors
            errors['codes'] = [code.errors for code in form.codes]
            logger.info('Failed saving paste for reason: %s', errors)
            return jsonify(success=False, errors=errors)


@paste_app.route('/<hash_id>/edit', methods=['GET', 'POST'])
@login_required
@user_active_required
def edit_paste(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)

    if not paste.is_user_owned(current_user.user):
        abort(404)

    if request.method == 'GET':
        tags = []
        syntaxes = [code.syntax.name for code in paste.codes]
        for tag in paste.tags:
            if tag.name not in syntaxes:
                tags.append(tag.name)
        data = {'hash_id': paste.hash_id,
                'title': paste.title,
                'is_private': paste.is_private,
                'tags': ','.join(tags),
                'codes': [{'title': code.title, 'content': code.content, 'syntax': code.syntax.key} for code in paste.codes]}
        return render_template('pastes/edit.html',
                               paste=paste,
                               data=data)
    else:
        form = PasteForm(request.form)
        if form.validate():
            paste = save_paste_and_codes(form, paste=paste)
            flash(u"代码集合已成功修改")
            return jsonify(success=True, hash_id=paste.hash_id)
        else:
            errors = form.errors
            errors['codes'] = [code.errors for code in form.codes]
            logger.info('Failed saving paste for reason: %s', errors)
            return jsonify(success=False, errors=errors)


@paste_app.route('/<hash_id>', methods=['GET'])
def view_paste(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)
    paste.increase_views()

    paste_lists = []
    if current_user.is_authenticated:
        paste_lists = Bookmark.objects(user=current_user.user)

    syntax_list = [code.syntax for code in paste.codes]
    related_pastes = Paste.objects(codes__syntax__in=syntax_list).order_by('-created_at')[:10]

    return render_template('pastes/view.html',
                           paste=paste,
                           related_pastes=related_pastes,
                           paste_lists=paste_lists)


@paste_app.route('/<hash_id>/comments', methods=['POST'])
def comments(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)

    form = CommentForm(request.form)
    if form.validate():
        comment = Comment(user=current_user.user,
                          paste=paste,
                          content=form.content.data)
        comment.save()
        if comment.user != paste.user:
            content = NEW_COMMENT.format(user_username=current_user.user.username,
                                         user_url=url_for('user_app.view', username=current_user.user.username),
                                         paste_title=paste.title,
                                         paste_url=url_for('paste_app.view_paste', hash_id=paste.hash_id))

            message = Message(user=paste.user,
                              who=current_user.user,
                              content=content)
            message.save()

    return redirect(url_for('paste_app.view_paste', hash_id=hash_id))


@paste_app.route('/<paste_id>/comments/<hash_id>', methods=['GET', 'POST'])
def edit_comment(paste_id, hash_id):
    comment = Comment.objects.get_or_404(hash_id=hash_id)
    form = CommentForm(request.form)
    if request.method == 'POST':
        if form.validate():
            comment.content = form.content.data
            comment.save()
            flash(u"评论已修改")
            return redirect(url_for('paste_app.view_paste', hash_id=paste_id))

    return render_template('pastes/edit_comment.html',
                           paste_id=paste_id,
                           comment=comment)


@paste_app.route('/<paste_id>/comments/<hash_id>/delete', methods=['GET'])
def delete_comment(paste_id, hash_id):
    comment = Comment.objects.get_or_404(hash_id=hash_id)
    comment.delete()
    flash(u"评论已删除")
    return redirect(url_for('paste_app.view_paste', hash_id=paste_id))


@paste_app.route('/<hash_id>/like', methods=['POST'])
@login_required
def like(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)
    user = current_user.user
    is_user_liked = paste in user.likes
    if not is_user_liked:
        user.likes.append(paste)
        user.save()
        if user != paste.user:
            content = LIKE.format(user_username=user.username,
                                  user_url=url_for('user_app.view', username=user.username),
                                  paste_title=paste.title,
                                  paste_url=url_for('paste_app.view_paste', hash_id=paste.hash_id))
            message = Message(user=paste.user,
                              who=user,
                              content=content)
            message.save()
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
        flash(u"代码集合已删除")
        return redirect('/')
    else:
        abort(403)


@paste_app.route('/<hash_id>/embed.js', methods=['GET'])
def embed_js(hash_id):
    paste = Paste.objects.get_or_404(hash_id=hash_id)

    resp = make_response(render_template('pastes/embed.html', paste=paste, domain=current_app.config['DOMAIN']), 200)
    resp.headers['Content-Type'] = 'text/javascript; charset=utf-8'
    return resp
