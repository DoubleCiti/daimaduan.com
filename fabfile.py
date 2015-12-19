import sys
from fabric.context_managers import cd
from fabric.context_managers import lcd
from fabric.operations import local
from fabric.operations import put
from fabric.operations import run
from fabric.operations import sudo
from fabric.state import env


env.colorize_errors = True
# the servers where the commands are executed
env.hosts = ['daimaduan.com']
# the user to use for the remote commands
env.user = 'daimaduan'
# application data
APP_NAME = 'daimaduan'


def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)


def bootstrap(app_env):
    if not app_env:
        print "fab pack deploy:<ENV>"
        sys.exit(1)

    app_path = '/var/www/%s/%s' % (APP_NAME, app_env)
    log_path = '/var/log/%s/%s' % (APP_NAME, app_env)
    sudo('mkdir -p %s' % app_path)
    sudo('chown %s:%s %s' % (env.user, env.user, app_path))
    sudo('mkdir -p %s' % log_path)
    sudo('chown %s:%s %s' % (env.user, env.user, log_path))
    with cd(app_path):
        run('virtualenv --distribute venv')


def deploy(app_env):
    if not app_env:
        print "fab pack deploy:<ENV>"
        sys.exit(1)

    app_path = '/var/www/%s/%s' % (APP_NAME, app_env)
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '%s/%s.tar.gz' % (app_path, dist))
    with cd(app_path):
        run('tar xzf %s.tar.gz' % dist)
    with cd('%s/%s' % (app_path, dist)):
        run('%s/venv/bin/python setup.py install > /dev/null 2>&1' % app_path)
    run('rm -f %s/current' % app_path)
    run('ln -s %s/%s/daimaduan %s/current' % (app_path, dist, app_path))
    run('cp %s/shared/config.cfg %s/current' % (app_path, app_path))
    run('cp %s/shared/deploy.py %s/current' % (app_path, app_path))

    # last step, touch uwsgi ini file to force reload uwsgi
    sudo('touch /etc/uwsgi.d/daimaduan_%s.ini' % app_env)

    run('rm -f %s/%s.tar.gz' % (app_path, dist))


def run_server():
    local('python setup.py develop')
    with lcd('daimaduan'):
        local('python runserver.py')


def seed():
    local('python setup.py develop')
    local('cp daimaduan/config.cfg config.cfg')
    from daimaduan.seed_data import seed_data
    seed_data()
    local('rm -f config.cfg')
