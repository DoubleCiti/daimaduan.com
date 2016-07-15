import re
from mongodb_migrations.base import BaseMigration


OLD_SUPPORTED_SYNTAX = (
    (u'bash', u'Bash'),
    (u'java', u'Java'),
    (u'cpp', u'C++'),
    (u'xml', u'XML'),
    (u'spec', u'RPMSpec'),
    (u'sql', u'SQL'),
    (u'json', u'JSON'),
    (u'sass', u'Sass'),
    (u'coffee-script', u'CoffeeScript'),
    (u'vim', u'VimL'),
    (u'scala', u'Scala'),
    (u'css', u'CSS'),
    (u'less', u'LESS'),
    (u'c', u'C'),
    (u'yaml', u'YAML'),
    (u'text', u'Text only'),
    (u'dart', u'Dart'),
    (u'diff', u'Diff'),
    (u'swift', u'Swift'),
    (u'js', u'JavaScript'),
    (u'puppet', u'Puppet'),
    (u'groovy', u'Groovy'),
    (u'gradle', u'Gradle'),
    (u'python', u'Python'),
    (u'scss', u'SCSS'),
    (u'lua', u'Lua'),
    (u'go', u'Go'),
    (u'perl', u'Perl'),
    (u'ini', u'INI'),
    (u'nginx', u'Nginx configuration file'),
    (u'php', u'PHP'),
    (u'erb', u'ERB'),
    (u'html', u'HTML'),
    (u'rst', u'reStructuredText'),
    (u'make', u'Makefile'),
    (u'rb', u'Ruby'),
    (u'docker', u'Docker'),
    (u'kotlin', u'Kotlin'),
    (u'erlang', u'Erlang'),
    (u'clojure', u'Clojure'),
    (u'csharp', u'C#'),
    (u'objective-c', u'Objective-C'),
    (u'haskell', u'Haskell')
)

NEW_SUPPORTED_SYNTAX = (
    ('accesslog', 'AccessLog'),
    ('actionscript', 'ActionScript'),
    ('apache', 'Apache'),
    ('applescript', 'AppleScript'),
    ('bash', 'Bash'),
    ('clojure', 'Clojure'),
    ('cmake', 'Cmake'),
    ('coffee-script', 'CoffeeScript'),
    ('cpp', 'C++'),
    ('csharp', 'C#'),
    ('css', 'CSS'),
    ('dart', 'Dart'),
    ('diff', 'Diff'),
    ('django', 'Django'),
    ('dockerfile', 'Dockerfile'),
    ('erb', 'Erb'),
    ('erlang', 'Erlang'),
    ('fsharp', 'FSharp'),
    ('go', 'Go'),
    ('gradle', 'Gradle'),
    ('groovy', 'Groovy'),
    ('haskell', 'Haskell'),
    ('http', 'HTTP'),
    ('html', 'HTML'),
    ('ini', 'INI'),
    ('java', 'Java'),
    ('javascript', 'JavaScript'),
    ('json', 'JSON'),
    ('kotlin', 'Kotlin'),
    ('less', 'LESS'),
    ('lisp', 'Lisp'),
    ('lua', 'Lua'),
    ('makefile', 'MakeFile'),
    ('markdown', 'Markdown'),
    ('matlab', 'Matlab'),
    ('nginx', 'Nginx'),
    ('objective-c', 'Objective-C'),
    ('perl', 'Perl'),
    ('php', 'PHP'),
    ('powershell', 'PowerShell'),
    ('protobuf', 'Protobuf'),
    ('puppet', 'Puppet'),
    ('python', 'Python'),
    ('ruby', 'Ruby'),
    ('rust', 'Rust'),
    ('scala', 'Scala'),
    ('scheme', 'Scheme'),
    ('scss', 'SASS/SCSS'),
    ('smalltalk', 'SmallTalk'),
    ('sql', 'SQL'),
    ('swift', 'Swift'),
    ('tex', 'Tex'),
    ('text', 'Text'),
    ('vbscript', 'VBScript'),
    ('vim', 'Vim'),
    ('xml', 'XML'),
    ('yaml', 'Yaml')
)

MAPPING = {
    'rb': 'ruby',
    'docker': 'dockerfile',
    'js': 'javascript',
    'make': 'makefile',
    'spec': 'text'
}


class Migration(BaseMigration):
    def upgrade(self):
        self.syntaxes = {}
        for syntax in self.db.syntax.find():
            self.syntaxes[str(syntax['_id'])] = syntax['key']

        self.db.syntax.drop()
        self.db.tag.drop()

        for syntax in NEW_SUPPORTED_SYNTAX:
            self.db.syntax.save({'key': syntax[0], 'name': syntax[1]})

        for paste in self.db.paste.find():
            paste['tags'] = []
            for code in paste['codes']:
                syntax_id = str(code['syntax'])
                syntax = self.get_syntax(syntax_id)
                code['syntax'] = syntax['_id']
                self.save_tag(syntax)
            self.db.paste.save(paste)

    def downgrade(self):
        print "I'm in downgrade - migration2"

    def get_syntax(self, syntax_id):
        key = self.syntaxes[syntax_id]
        if key in MAPPING:
            key = MAPPING[key]

        return self.db.syntax.find_one({'key': key})

    def save_tag(self, syntax):
        tag = self.db.tag.find_one({'key': syntax['key']})
        if not tag:
            self.db.tag.save({'key': syntax['key'], 'name': syntax['name']})
