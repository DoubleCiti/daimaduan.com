from flask import Blueprint
from flask import render_template
from flask import request
from flask.ext.login import current_user

from daimaduan.models.base import Paste
from daimaduan.models.syntax import Syntax
from daimaduan.models.tag import Tag
from daimaduan.utils.pagination import get_page


tag_app = Blueprint('tag_app', __name__, template_folder="templates")


@tag_app.route('/<tag_name>', methods=['GET'])
def view(tag_name):
    criteria = {}
    tag = Tag.objects.get_or_404(key=tag_name)
    if request.args.get('filter', None) != 'mine' or not current_user.is_authenticated:
        criteria['is_private'] = False
    syntax = Syntax.objects(key=tag_name).first()
    if syntax:
        criteria['codes__syntax'] = syntax
    else:
        criteria['tags'] = tag
    pastes = Paste.objects(**criteria).order_by('-updated_at')
    page = get_page()

    pagination = pastes.paginate(page, per_page=20)

    return render_template('tags/view.html',
                           tag=tag,
                           hot_pastes=Paste.objects(is_private=False).order_by('-views')[:10],
                           pagination=pagination)
