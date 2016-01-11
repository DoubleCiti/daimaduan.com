#
# @app.hook('before_request')
# def before_request():
#     request.user = login.get_user()
#
#
# @app.hook('after_request')
# def after_request():
#     Jinja2Template.defaults['session'] = request.environ.get('beaker.session')
#
#
