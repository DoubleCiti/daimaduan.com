from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask.ext.login import current_user, login_required

from daimaduan.forms.paste_list import PasteListForm
from daimaduan.models.base import Paste
from daimaduan.models.paste_list import PasteList
from daimaduan.utils.pagination import get_page


list_app = Blueprint("list_app", __name__, template_folder="templates")


@list_app.route('/', methods=['GET'])
def index():
    page = get_page()

    pagination = PasteList.objects(is_private=False).paginate(page, per_page=20)

    return render_template('lists/index.html',
                           pagination=pagination)


@list_app.route('/create', methods=['GET', 'POST'])
@login_required
def create_list():
    form = PasteListForm()
    if request.method == 'GET':
        return render_template('lists/create.html',
                               form=form)
    else:
        if form.validate_on_submit():
            paste_list = PasteList(title=form.title.data,
                                   is_private=form.is_private.data,
                                   description=form.description.data,
                                   user=current_user.user)
            paste_list.save()

            return redirect(url_for('list_app.view_list', hash_id=paste_list.hash_id))
        return render_template('lists/create.html',
                               form=form)


@list_app.route('/add_paste', methods=['POST'])
@login_required
def add_paste():
    if 'paste_hash_id' not in request.form or 'paste_list_id' not in request.form:
        abort(404)
    paste_list = PasteList.objects(hash_id=request.form['paste_list_id']).get_or_404()
    paste = Paste.objects(hash_id=request.form['paste_hash_id']).get_or_404()
    if paste not in paste_list.pastes:
        paste_list.pastes.append(paste)
        paste_list.save()

    return redirect(url_for('list_app.view_list', hash_id=paste_list.hash_id))


@list_app.route('/<hash_id>/delete', methods=['POST'])
@login_required
def delete_list(hash_id):
    paste_list = PasteList.objects(hash_id=hash_id).get_or_404()
    if paste_list.user != current_user.user:
        abort(401)
    paste_list.delete()

    return redirect(url_for('list_app.index'))


@list_app.route('/<hash_id>', methods=['GET'])
def view_list(hash_id):
    paste_list = PasteList.objects(hash_id=hash_id).get_or_404()

    return render_template('lists/view.html',
                           paste_list=paste_list)
