# coding: utf-8

from pygments.lexers import get_all_lexers
from daimaduan.bootstrap import app
from daimaduan.models.syntax import Syntax
from operator import itemgetter


def lexer_parser(lexer):
    return {"name": lexer[0], "key": lexer[1][0]}


def get_lexers():
    lexers = map(lexer_parser, get_all_lexers())
    return sorted(lexers, key=itemgetter("name"))


def generate():
    lexers = get_lexers()
    for lexer in lexers:
        print lexer
        Syntax.find_or_create_by(**lexer)


if __name__ == "__main__":
    generate()
