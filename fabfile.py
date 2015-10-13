from fabric.api import *


env.colorize_errors = True
# the servers where the commands are executed
env.hosts = ['daimaduan.com']
# the user to use for the remote commands
env.user = 'daimaduan'
# application data
APP_ENV = 'preview'
APP_NAME = 'daimaduan'
APP_PATH = '/var/www/%s/%s' % (APP_NAME, APP_ENV)
TEMP_PATH = '/tmp/%s/%s' % (APP_NAME, APP_ENV)
LOG_PATH = '/var/log/%s/%s' % (APP_NAME, APP_ENV)


def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)


def bootstrap():
    sudo('mkdir -p %s' % APP_PATH)
    sudo('chown %s:%s %s' %(env.user, env.user, APP_PATH))
    sudo('mkdir -p %s' % LOG_PATH)
    sudo('chown %s:%s %s' %(env.user, env.user, LOG_PATH))
    with cd(APP_PATH):
        run('virtualenv --distribute venv')


def deploy():
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '%s/%s.tar.gz' % (APP_PATH, dist))
    with cd(APP_PATH):
        run('tar xzf %s.tar.gz' % dist)
    with cd('%s/%s' % (APP_PATH, dist)):
        run('%s/venv/bin/python setup.py install > /dev/null 2>&1' % APP_PATH)
    run('rm -f %s/current' % APP_PATH)
    run('ln -s %s/%s/daimaduan %s/current' % (APP_PATH, dist, APP_PATH))
    run('cp %s/shared/config.cfg %s/current' % (APP_PATH, APP_PATH))
    run('cp %s/shared/deploy.wsgi %s/current' % (APP_PATH, APP_PATH))

    # last step, touch uwsgi ini file to force reload uwsgi
    sudo('touch /etc/uwsgi.d/daimaduan_%s.ini' % APP_ENV)

    run('rm -f %s/%s.tar.gz' % (APP_PATH, dist))
