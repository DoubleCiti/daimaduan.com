# coding: utf-8
import datetime
import json
import re

from flask import abort
from flask import Blueprint, flash, current_app, session, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.login import login_required
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from rauth import OAuth2Service

from daimaduan.bootstrap import login_manager
from daimaduan.forms.email import EmailForm
from daimaduan.forms.password import PasswordForm
from daimaduan.forms.signin import SigninForm
from daimaduan.forms.signup import SignupForm
from daimaduan.forms.userinfo import UserInfoForm
from daimaduan.models import LoginManagerUser
from daimaduan.models.base import Code
from daimaduan.models.base import Paste
from daimaduan.models.base import User
from daimaduan.models.bookmark import Bookmark
from daimaduan.models.tag import Tag
from daimaduan.models.message import Message
from daimaduan.models.user_oauth import UserOauth
from daimaduan.utils.email_confirmation import send_confirm_email
from daimaduan.utils.email_confirmation import send_reset_password_email
from daimaduan.utils.email_confirmation import validate_token
from daimaduan.utils.oauth import oauth_config
from daimaduan.utils.pagination import get_page


def get_oauth_services():
    oauth_services = {}
    oauth_services['google'] = OAuth2Service(**oauth_config(current_app.config, 'google'))
    oauth_services['github'] = OAuth2Service(**oauth_config(current_app.config, 'github'))
    return oauth_services


@login_manager.user_loader
def load_user(user_id):
    user = User.objects.get_or_404(id=user_id)
    return LoginManagerUser(user)


site_app = Blueprint("site_app", __name__, template_folder="templates")


@site_app.route('/', methods=['GET'])
def index():
    page = get_page()
    pagination = Paste.objects(is_private=False).order_by('-updated_at').paginate(page=page, per_page=20)

    return render_template('index.html',
                           pagination=pagination,
                           tags=Tag.objects().order_by('-popularity')[:10])


@site_app.route('/tags', methods=['GET'])
def tags():
    return render_template('tags/index.html',
                           tags=Tag.objects().order_by('-popularity'))


@site_app.route('/status.json', methods=['GET'])
def status():
    return jsonify(version=current_app.config['VERSION'],
                   pastes=Paste.objects().count(),
                   bookmarks=Bookmark.objects().count(),
                   tags=Tag.objects().count(),
                   users=User.objects().count())


@site_app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if request.method == 'GET':
        return render_template('users/signin.html',
                               form=SigninForm())
    else:
        if form.validate_on_submit():
            user = User.objects.get_or_404(email=form.email.data)
            user_mixin = LoginManagerUser(user)
            login_user(user_mixin)

            flash('Logged in successfully.')

            return redirect(url_for('site_app.index'))
        return render_template('users/signin.html',
                               form=form)


@site_app.route('/signout', methods=['DELETE'])
def signout_delete():
    logout_user()
    return jsonify(status=302, location="/")


@site_app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('users/signup.html',
                               form=form)
    else:
        if form.validate_on_submit():
            user = User()
            form.populate_obj(user)
            user.save()
            bookmark = Bookmark(user=user,
                                title=u"%s 的收藏夹" % user.username,
                                is_default=True)
            bookmark.save()
            user_mixin = LoginManagerUser(user)
            login_user(user_mixin)
            send_confirm_email(current_app.config, user.email)
            return redirect(url_for('site_app.index'))
        return render_template('users/signup.html',
                               form=form)


@site_app.route('/oauth/<provider>', methods=['GET'])
def oauth_signin(provider):
    oauth_service = get_oauth_services()[provider]

    url = oauth_service.get_authorize_url(scope=current_app.config['OAUTH'][provider]['scope'],
                                          response_type='code',
                                          redirect_uri=current_app.config['OAUTH'][provider]['callback_url'])
    return redirect(url)


@site_app.route('/oauth/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    current_app.logger.info("Oauth callback for %s" % provider)
    redirect_uri = current_app.config['OAUTH'][provider]['callback_url']
    oauth_service = get_oauth_services()[provider]

    data = dict(code=request.args.get('code'),
                grant_type='authorization_code',
                redirect_uri=redirect_uri)

    if provider == 'google':
        oauth_session = oauth_service.get_auth_session(data=data, decoder=json.loads)
        user_info = oauth_session.get('userinfo').json()
        email = session['email'] = user_info['email']
        username = user_info['given_name']
    elif provider == 'github':
        oauth_session = oauth_service.get_auth_session(data=data)
        user_info = oauth_session.get('user').json()
        email = session['email'] = user_info['email']
        username = user_info['login']

    access_token = oauth_session.access_token
    user_info['id'] = str(user_info['id'])

    current_app.logger.info("%s oauth access token is: %s" % (provider, access_token))
    current_app.logger.info("%s oauth user info is %s" % (provider, user_info))

    user = User.find_by_oauth(provider, user_info['id'])
    if user:
        # TODO: 直接登录时更新 token.
        user_mixin = LoginManagerUser(user)
        login_user(user_mixin)
        return redirect('/')
    else:
        user = User.objects(email=email).first()
        if user:
            user_oauth = UserOauth(provider=provider, openid=user_info['id'], token=access_token)
            user_oauth.save()
            user_mixin = LoginManagerUser(user)
            login_user(user_mixin)
            return redirect('/')
        else:
            return render_template('users/manage.html',
                                   form=UserInfoForm(email=email, username=username))


@site_app.route('/lost_password', methods=['GET', 'POST'])
def lost_password_get():
    if request.method == 'GET':
        return render_template('users/lost_password.html',
                               form=EmailForm())
    else:
        form = EmailForm(request.form)
        if form.validate():
            user = User.objects(email=form.email.data).first()
            send_reset_password_email(current_app.config, user.email)
            return redirect('/reset_password_email_sent')
        return render_template('users/lost_password.html',
                               form=form)


@site_app.route('/reset_password_email_sent', methods=['GET'])
def reset_password_email_sent():
    return render_template('error.html',
                           title=u"重置密码的邮件已经发出",
                           message=u"重置密码的邮件已经发出, 请查收邮件并重置密码")


@site_app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        email = validate_token(current_app.config, token)
        if email:
            user = User.objects(email=email).first()
            if user:
                return render_template('users/reset_password.html',
                                       form=PasswordForm(),
                                       token=token)
        abort(404)
    else:
        email = validate_token(current_app.config, token)
        if email:
            user = User.objects(email=email).first()
            if user:
                form = PasswordForm(request.form)
                if form.validate_on_submit():
                    user.password = user.generate_password(form.password.data)
                    user.save()
                    return redirect('/reset_password_success')
                return render_template('users/reset_password.html',
                                       form=PasswordForm(),
                                       token=token)
        abort(404)


@site_app.route('/reset_password_success', methods=['GET'])
def reset_password_success():
    return render_template('error.html',
                           title=u"重置密码成功",
                           message=u"您的密码已经重置, 请重新登录")


@site_app.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    email = validate_token(current_app.config, token)
    if email:
        user = User.objects(email=email).first_or_404()
        if (current_user.is_authenticated and user == current_user.user) or not current_user.is_authenticated:
            if user.is_email_confirmed:
                return render_template('email/confirm.html', title=u"Email已经激活过了", message=u"对不起，您的email已经激活过了。")
            else:
                user.is_email_confirmed = True
                user.email_confirmed_on = datetime.datetime.now()
                user.save()
                return render_template('email/confirm.html', title=u'Email已经激活', message=u'您的email已经激活，请点击登录查看最新代码段。')
    return render_template('email/confirm.html',
                           title=u'Email验证链接错误',
                           message=u'对不起，您的验证链接无效或者已经过期。')


@site_app.route('/active_email', methods=['GET'])
def active_email():
    return render_template('email/active.html',
                           email=current_user.user.email,
                           title=u'注册成功')


@site_app.route('/success_sendmail', methods=['GET'])
def sendmail_success():
    return render_template('email/confirm.html',
                           title=u"激活邮件发送成功",
                           message=u"激活邮件发送成功, 请检查并激活您的账户。")


@site_app.route('/sendmail', methods=['POST'])
def send_email():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        send_confirm_email(current_app.config, user.email)
        return redirect('/success_sendmail')
    return render_template('sendmail.html',
                           form=form)


def get_pastes_from_search(query_string, p=1):
    def get_string_by_keyword(keyword, query_string):
        string = ''
        result = re.search('\s*%s:([a-zA-Z+-_#]+)\s*' % keyword, query_string)
        if result:
            if len(result.groups()) == 1:
                string = result.groups()[0]
        return string, query_string.replace('%s:%s' % (keyword, string), '')

    tag, query_string = get_string_by_keyword('tag', query_string)
    user, query_string = get_string_by_keyword('user', query_string)
    keyword = query_string.strip()

    criteria = {'title__contains': keyword, 'is_private': False}
    if tag:
        criteria['tags'] = tag
    if user:
        user_object = User.objects(username=user).first()
        if user_object:
            criteria['user'] = user_object

    return keyword, Paste.objects(**criteria).order_by('-updated_at').paginate(p, per_page=2)


@site_app.route('/search', methods=['GET'])
def search_paste():
    page = get_page()
    q = request.args['q']
    keyword, pagination = get_pastes_from_search(q, p=page)
    return render_template('search.html',
                           query_string=q,
                           keyword=keyword,
                           pagination=pagination)


@site_app.route('/messages', methods=['GET'])
@login_required
def messages():
    page = get_page()
    pagination = Message.objects(user=current_user.user).order_by('-created_at').paginate(page, per_page=20)
    for item in pagination.items:
        item.is_read = True
        item.save()
    return render_template('users/messages.html',
                           pagination=pagination)
