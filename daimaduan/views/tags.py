from flask import Blueprint
from flask import render_template

from daimaduan.models.tag import Tag
from daimaduan.utils.pagination import get_page


tag_app = Blueprint('tag_app', __name__, template_folder="templates")


@tag_app.route('/<tag_name>', methods=['GET'])
def view(tag_name):
    tag = Tag.objects.get_or_404(name=tag_name)
    page = get_page()

    pastes = tag.pastes(is_private=False).order_by('-updated_at')
    pagination = pastes.paginate(page, per_page=20)

    return render_template('tags/view.html',
                           tag=tag,
                           pagination=pagination)
