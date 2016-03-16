# coding: utf-8
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask.ext.login import current_user, login_required

from daimaduan.forms.bookmark import BookmarkForm
from daimaduan.models.base import Paste
from daimaduan.models.bookmark import Bookmark
from daimaduan.utils.pagination import get_page


bookmark_app = Blueprint("bookmark_app", __name__, template_folder="templates")


@bookmark_app.route('/', methods=['GET'])
def index():
    page = get_page()

    pagination = Bookmark.objects(is_private=False).order_by('-updated_at').paginate(page, per_page=20)

    return render_template('bookmarks/index.html',
                           pagination=pagination)


@bookmark_app.route('/mine', methods=['GET'])
@login_required
def my_list():
    page = get_page()

    pagination = Bookmark.objects(user=current_user.user).order_by('-updated_at').paginate(page, per_page=20)

    return render_template('bookmarks/index.html',
                           pagination=pagination)


@bookmark_app.route('/create', methods=['GET', 'POST'])
@login_required
def create_list():
    form = BookmarkForm()
    if request.method == 'GET':
        return render_template('bookmarks/create.html',
                               form=form)
    else:
        if form.validate_on_submit():
            paste_list = Bookmark(title=form.title.data,
                                  is_private=form.is_private.data,
                                  description=form.description.data,
                                  user=current_user.user)
            paste_list.save()

            return redirect(url_for('bookmark_app.view_list', hash_id=paste_list.hash_id))
        return render_template('bookmarks/create.html',
                               form=form)


@bookmark_app.route('/add_paste', methods=['POST'])
@login_required
def add_paste():
    if 'paste_hash_id' not in request.form or 'paste_list_id' not in request.form:
        abort(404)
    paste_list = Bookmark.objects(hash_id=request.form['paste_list_id']).get_or_404()
    paste = Paste.objects(hash_id=request.form['paste_hash_id']).get_or_404()
    if paste in paste_list.pastes:
        return render_template('error.html',
                               title=u'该代码集合已经在收藏夹中',
                               message=u'该代码集合已经在收藏夹中')
    if len(paste_list.pastes) >= 10:
        return render_template('error.html',
                               title=u'一个收藏夹最多只能有10个代码集合',
                               message=u'一个收藏夹最多只能有10个代码集合')
    if paste not in paste_list.pastes:
        paste_list.pastes.append(paste)
        paste_list.save()

    return redirect(url_for('bookmark_app.view_list', hash_id=paste_list.hash_id))


@bookmark_app.route('/<hash_id>/delete', methods=['POST'])
@login_required
def delete_list(hash_id):
    paste_list = Bookmark.objects(hash_id=hash_id).get_or_404()
    if paste_list.user != current_user.user:
        abort(401)
    paste_list.delete()

    return redirect(url_for('bookmark_app.index'))


@bookmark_app.route('/<hash_id>', methods=['GET'])
def view_list(hash_id):
    paste_list = Bookmark.objects(hash_id=hash_id).get_or_404()

    return render_template('bookmarks/view.html',
                           paste_list=paste_list)
