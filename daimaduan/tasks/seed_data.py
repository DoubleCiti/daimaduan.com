import json
from operator import itemgetter

from fabric.decorators import task

from daimaduan.models.syntax import Syntax


DIST_FILE = 'daimaduan/static/js/lexers.js'


ALL_SUPPORTED_SYNTAX = (
    ('accesslog', 'AccessLog'),
    ('actionscript', 'ActionScript'),
    ('apache', 'Apache'),
    ('applescript', 'AppleScript'),
    ('bash', 'Bash'),
    ('clojure', 'Clojure'),
    ('cmake', 'Cmake'),
    ('coffeescript', 'CoffeeScript'),
    ('cpp', 'C++'),
    ('cs', 'C#'),
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
    ('ini', 'INI'),
    ('java', 'Java'),
    ('javascript', 'JavaScript'),
    ('json', 'Json'),
    ('kotlin', 'Kotlin'),
    ('less', 'LESS'),
    ('lisp', 'Lisp'),
    ('lua', 'Lua'),
    ('makefile', 'MakeFile'),
    ('markdown', 'Markdown'),
    ('matlab', 'Matlab'),
    ('nginx', 'Nginx'),
    ('objectivec', 'Objective-C'),
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
    ('vbscript', 'VBScript'),
    ('vim', 'Vim'),
    ('xml', 'XML'),
    ('yaml', 'Yaml')
)


def lexer_parser(lexer):
    return {"name": lexer[1], "value": lexer[0]}


def get_lexers():
    lexers = map(lexer_parser, ALL_SUPPORTED_SYNTAX)
    return sorted(lexers, key=itemgetter("name"))


def lexer_dumps(lexer):
    return json.dumps(lexer)


@task
def seed():
    """Seed syntax data in MongoDB"""
    def find_or_create_syntax(key, name):
        syn = Syntax.objects(key=key).first()
        if syn is None:
            print "Seeding syntax: %s, %s" % (key, name)
            Syntax(key=key, name=name).save()

    for key, name in ALL_SUPPORTED_SYNTAX:
        find_or_create_syntax(key, name)

    print "Generating %s" % DIST_FILE
    with open(DIST_FILE, "w") as f:
        lexers = get_lexers()
        lexers_code = ", ".join(map(lexer_dumps, lexers))
        f.write("var lexers = [%s];" % lexers_code)
        print "  %d lexers created." % len(lexers)
