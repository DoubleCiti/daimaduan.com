from fabric.decorators import task

from daimaduan.bootstrap import app


@task
def run():
    """Start development server"""
    app.run(host="0.0.0.0", port=8080)
