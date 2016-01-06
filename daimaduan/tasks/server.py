from fabric.decorators import task
from fabric.operations import local

from bottle import run
from bottle import static_file

from daimaduan.bootstrap import get_current_path
from daimaduan import app
from daimaduan import application


@task
def serve():
    """Start development server"""
    local('python setup.py install')

    @app.route('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root='%s/static' % get_current_path())

    run(application,
        host='0.0.0.0',
        port=8080,
        debug=True,
        reloader=True)
