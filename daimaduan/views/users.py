# coding: utf-8
from daimaduan.models.syntax import Syntax
from flask import Blueprint, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.mongoengine import Pagination
from flask_login import current_user
from flask_login import login_required

from daimaduan.forms.userinfo import UserInfoForm
from daimaduan.models.base import User
from daimaduan.models.base import Paste
from daimaduan.models.bookmark import Bookmark
from daimaduan.models.message import WATCH
from daimaduan.models.message import Message
from daimaduan.models.tag import Tag
from daimaduan.utils.pagination import get_page

user_app = Blueprint("user_app", __name__, template_folder="templates")


@user_app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    form = UserInfoForm(data=dict(username=current_user.user.username,
                                  email=current_user.user.email,
                                  description=current_user.user.description))
    if request.method == 'POST':
        form = UserInfoForm(request.form)
        if form.validate():
            current_user.user.username = form.username.data
            current_user.user.description = form.description.data
            current_user.user.save()
            return redirect(url_for('user_app.manage'))
    return render_template('users/manage.html',
                           form=form)


def get_most_syntax(syntax):
    highest_name = None
    for name in syntax:
        if not highest_name:
            highest_name = name
        else:
            if syntax[name] > syntax[highest_name]:
                highest_name = name
    syntax.pop(highest_name)
    return Syntax.objects(name=highest_name).first()


@user_app.route('/<username>', methods=['GET'])
def view(username):
    page = get_page()
    user = User.objects.get_or_404(username=username)

    pastes = user.pastes.order_by('-updated_at')
    if not (current_user.is_authenticated and current_user.user == user):
        pastes = pastes(is_private=False)

    pagination = pastes.paginate(page, per_page=20)

    pastes = Paste.objects(user=user)
    syntax = {}
    for paste in pastes:
        for code in paste.codes:
            if code.syntax.name not in syntax:
                syntax[code.syntax.name] = 1
            else:
                syntax[code.syntax.name] += 1

    if len(syntax.keys()) > 3:
        most_syntax = [get_most_syntax(syntax) for i in range(3)]
    else:
        most_syntax = [Syntax.objects(name=key).first() for key in syntax]

    return render_template('users/user.html',
                           user=user,
                           pagination=pagination,
                           most_syntax=most_syntax,
                           tags=Tag.objects().order_by('-popularity')[:10])


@user_app.route('/<username>/followings', methods=['GET'])
def view_followings(username):
    page = get_page()
    user = User.objects.get_or_404(username=username)

    pagination = Pagination(user.followings, page, per_page=20)

    return render_template('users/followings.html',
                           user=user,
                           pagination=pagination)


@user_app.route('/<username>/followers', methods=['GET'])
def view_followers(username):
    page = get_page()
    user = User.objects.get_or_404(username=username)

    pagination = User.objects(followings=user).paginate(page, per_page=20)

    return render_template('users/followers.html',
                           user=user,
                           pagination=pagination)


@user_app.route('/<username>/likes', methods=['GET'])
def view_likes(username):
    user = User.objects.get_or_404(username=username)

    page = get_page()
    likes = Paste.objects(id__in=[str(i.id) for i in user.likes]).order_by('-updated_at')
    pagination = likes.paginate(page, per_page=20)

    return render_template('users/likes.html',
                           user=user,
                           pagination=pagination)


@user_app.route('/<username>/watch', methods=['POST'])
@login_required
def watch_user(username):
    following_user = User.objects(username=username).first_or_404()

    if not current_user.user.is_following(following_user):
        current_user.user.followings.append(following_user)
        current_user.user.save()

        content = WATCH.format(user_username=current_user.user.username,
                               user_url=url_for('user_app.view', username=current_user.user.username))
        message = Message(user=following_user,
                          who=current_user.user,
                          content=content)
        message.save()

    return jsonify(watchedStatus=current_user.user.is_following(following_user))


@user_app.route('/<username>/unwatch', methods=['POST'])
@login_required
def unwatch_user(username):
    following_user = User.objects(username=username).first_or_404()

    if current_user.user.is_following(following_user):
        current_user.user.followings.remove(following_user)
        current_user.user.save()

    return jsonify(watchedStatus=current_user.user.is_following(following_user))
