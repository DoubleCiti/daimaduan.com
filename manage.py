from flask.ext.script import Manager
from flask.ext.script import Server
from flask.ext.assets import ManageAssets

from daimaduan.bootstrap import app

manager = Manager(app)

# Keep the following line for issue https://github.com/miracle2k/flask-assets/issues/85
app.jinja_env.assets_environment.environment = app.jinja_env.assets_environment
manager.add_command("assets", ManageAssets(app.jinja_env.assets_environment))
manager.add_command("runserver", Server(host="0.0.0.0", port=8080))

if __name__ == "__main__":
    manager.run()
