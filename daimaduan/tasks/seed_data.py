from fabric.decorators import task
from fabric.operations import local
from daimaduan.models import Syntax


syntax_list = [
    "CSS",
    "JavaScript",
    "Objective-C",
    "Ruby",
    "Bash",
    "CoffeeScript",
    "INI",
    "Makefile",
    "PHP",
    "SQL",
    "C#",
    "Diff",
    "JSON",
    "Perl",
    "C++",
    "HTML",
    "XML",
    "Java",
    "Nginx",
    "Python",
    "Scala",
    "Vim-Script",
    "SCSS",
    "LESS",
    "Dockerfile",
    "Puppet",
    "Lua",
    "Gradle",
    "Go",
    "Dart",
    "Groovy",
    "VBScript",
    "Swift",
    "Access-Log",
    "Text"
]


@task
def seed():
    """Seed syntax data in MongoDB"""
    local('python setup.py install')

    def find_or_create_syntax(name):
        syntax = Syntax.objects(name=name).first()
        if syntax is None:
            print "Seeding syntax: %s" % name
            Syntax(name=name).save()

    for syntax in syntax_list:
        find_or_create_syntax(syntax)
