from webassets import Bundle
from webassets import Environment

my_env = Environment(
    directory='daimaduan/static',
    url='/static'
)

js = Bundle('js/app.js',
            'js/errors.js',
            'js/highlightjs.line.numbers.min.js',
            'js/pastes.js',
            'js/tags.js',
            'js/users.js',
            filters='uglifyjs', output='js/compiled.js')
my_env.register('js_all', js)

css = Bundle('css/app.css',
             'css/errors.css',
             'css/pastes.css',
             'css/tags.css',
             'css/users.css',
             filters='cssmin', output='css/compiled.css')
my_env.register('css_all', css)
