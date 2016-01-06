import mongoengine


class MongoenginePlugin(object):
    name = 'mongoengine_ext'
    api = 2

    def setup(self, app):
        self.app = app
        mongoengine.connect(app.config['mongoengine.database'],
                            host=app.config['mongoengine.host'])

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            return callback(*args, **kwargs)
        return wrapper
