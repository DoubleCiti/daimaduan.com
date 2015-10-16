from bottle import run
from bottle import static_file

from daimaduan import app
from daimaduan import application


if __name__ == '__main__':
    @app.route('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root='./static')

    run(application, host='0.0.0.0',
                     port=8080,
                     reloader=True)
