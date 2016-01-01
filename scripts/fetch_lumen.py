# coding: utf-8

from urlparse import urljoin
import urllib2
from tempfile import NamedTemporaryFile
import re
import os
from distutils.file_util import copy_file

BASE_URL = 'https://cdnjs.cloudflare.com/ajax/libs/bootswatch'
VERSION = '3.3.6'
THEME = 'lumen'
PAT_URL = r"url\(\'(?P<URL>.+?)\'\)"
DIST_FILE = 'daimaduan/static/css/bootstrap.min.css'


def has_gfw(line):
    return 'fonts.googleapis.com' in line


def has_url(line):
    return 'url(' in line


def theme_file_url(filename):
    return '%s/%s/%s/%s' % (BASE_URL, VERSION, THEME, filename)


def expand_url(match):
    relative_url = match.group('URL')
    full_url = urljoin(theme_file_url('foo.bar'), relative_url)
    print 'Process %s' % relative_url
    print '  ==> %s' % full_url
    return "url('%s')" % full_url


def expend_urls(line):
    return re.sub(PAT_URL, expand_url, line)


def fetch_lumen(version='3.3.6'):
    url = theme_file_url('bootstrap.min.css')

    print 'Fetching %s' % url
    response = urllib2.urlopen(url)

    with NamedTemporaryFile() as f:
        for line in response:
            if has_gfw(line):
                print 'Dropped gfw content: %s' % line,
            elif has_url(line):
                f.write(expend_urls(line))
            else:
                f.write(line)
        f.flush()

        print 'Updating site static %s' % DIST_FILE
        copy_file(f.name, DIST_FILE)


if __name__ == '__main__':
    fetch_lumen()
