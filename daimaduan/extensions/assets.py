from flask_assets import Bundle
from flask_assets import Environment

assets = Environment()

js = Bundle('lib/vue/dist/vue.js',
            'lib/lodash/lodash.js',
            'lib/clipboard/dist/clipboard.min.js',
            'lib/selectize/dist/js/standalone/selectize.js',
            'lib/highlightjs/highlight.pack.js',
            'js/lexers.js',
            'js/app.js',
            'js/pastes.js',
            filters='uglifyjs', output='js/compiled.js')
assets.register('js_all', js)

scss = Bundle('css/app.scss',
              'css/pastes.scss',
              'css/embed.scss',
              filters='scss', output='css/app.css')

css = Bundle('lib/selectize/dist/css/selectize.css',
             'lib/selectize/dist/css/selectize.bootstrap3.css',
             'css/bootstrap.min.css',
             'css/styles/foundation.css',
             scss,
             filters='cssmin', output='css/compiled.css')

assets.register('css_all', css)

embed = Bundle('css/embed.scss', filters='scss,cssmin', output='css/embed.css')

assets.register('embed', embed)
