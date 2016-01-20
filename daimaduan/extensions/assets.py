from flask_assets import Bundle
from flask_assets import Environment

assets = Environment()

js = Bundle('js/app.js',
            'js/pastes.js',
            filters='uglifyjs', output='js/compiled.js')
assets.register('js_all', js)

css = Bundle('css/app.scss',
             'css/pastes.scss',
             # 'css/embed.scss',
             filters='scss', output='css/compiled.css')

assets.register('css_all', css)
