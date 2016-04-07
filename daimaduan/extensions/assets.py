from flask_assets import Bundle
from flask_assets import Environment

assets = Environment()

js = Bundle('lib/vue/dist/vue.js',
            'lib/underscore/underscore.js',
            'js/lexers.js',
            'js/app.js',
            'js/pastes.js',
            filters='uglifyjs', output='js/compiled.js')
assets.register('js_all', js)

scss = Bundle('css/app.scss',
              'css/pastes.scss',
              'css/embed.scss',
              filters='scss')

css = Bundle('css/bootstrap.min.css',
             'css/colorful.min.css',
             scss,
             filters='cssmin', output='css/compiled.css')

assets.register('css_all', css)

embed = Bundle('css/embed.scss', filters='scss,cssmin', output='css/embed.css')

assets.register('embed', embed)
