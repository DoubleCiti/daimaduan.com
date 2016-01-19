# coding: utf-8

import json
from pygments.lexers import get_all_lexers
from operator import itemgetter


DIST_FILE = 'daimaduan/static/js/lexers.js'


def lexer_parser(lexer):
    return {"name": lexer[0], "value": lexer[1][0]}


def get_lexers():
    lexers = map(lexer_parser, get_all_lexers())
    return sorted(lexers, key=itemgetter("name"))


def lexer_dumps(lexer):
    return json.dumps(lexer)


def generate():
    print "Generating %s" % DIST_FILE
    with open(DIST_FILE, "w") as f:
        lexers = get_lexers()
        lexers_code = ", ".join(map(lexer_dumps, lexers))
        f.write("var lexers = [%s];" % lexers_code)
        print "  %d lexers created." % len(lexers)


if __name__ == "__main__":
    generate()
