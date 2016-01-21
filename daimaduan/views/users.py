# coding: utf-8
from flask import Blueprint, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask_login import current_user, login_required
from flask_login import login_user

from daimaduan.forms.userinfo import UserInfoForm
from daimaduan.models import LoginManagerUser
from daimaduan.models.base import User, Paste
from daimaduan.models.tag import Tag
from daimaduan.utils.pagination import get_page

user_app = Blueprint("user_app", __name__, template_folder="templates")


@user_app.route('/manage', methods=['POST'])
def manage():
    form = UserInfoForm(request.form)
    if form.validate():
        if current_user.is_authenticated:
            current_user.user.username = form.username.data
            return redirect('/')
        else:
            user = User(email=form.email.data, username=form.username.data,
                        is_email_confirmed=True)
            user.save()
            user_mixin = LoginManagerUser(user)
            login_user(user_mixin)
            if 'email' in session:
                del(session['email'])
            return redirect('/')
    return render_template('users/manage.html',
                           form=form)


@user_app.route('/<username>', methods=['GET'])
def view_user(username):
    page = get_page()
    user = User.objects.get_or_404(username=username)

    pastes = user.pastes.order_by('-updated_at')
    if not (current_user.is_authenticated and current_user.user == user):
        pastes = pastes(is_private=False)

    pagination = pastes.paginate(page, per_page=20)

    return render_template('users/user.html',
                           user=user,
                           pagination=pagination,
                           tags=Tag.objects().order_by('-popularity')[:10])


@user_app.route('/<username>/likes', methods=['GET'])
def view_likes(username):
    user = User.objects.get_or_404(username=username)

    page = get_page()
    likes = Paste.objects(id__in=[str(i.id) for i in user.likes]).order_by('-updated_at')
    pagination = likes.paginate(page, per_page=20)

    return render_template('users/likes.html',
                           user=user,
                           pagination=pagination)


@user_app.route('/watch', methods=['POST'])
def watch_user():
    be_followed_user = User.objects(username=request.form.get('user')).first_or_404()

    if not be_followed_user.is_followed_by(current_user.user):
        be_followed_user.followers.append(current_user.user)
        be_followed_user.save()

    return jsonify(watchedStatus=be_followed_user.is_followed_by(current_user.user))


@user_app.route('/unwatch', methods=['POST'])
def unwatch_user():
    be_followed_user = User.objects(username=request.form.get('user')).first_or_404()

    if be_followed_user.is_followed_by(current_user.user):
        be_followed_user.followers.remove(current_user.user)
        be_followed_user.save()

    return jsonify(watchedStatus=be_followed_user.is_followed_by(current_user.user))
