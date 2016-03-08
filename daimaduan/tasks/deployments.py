import sys
import urllib2

from fabric.context_managers import cd
from fabric.decorators import task
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
TEST_WEBSITE = {
    'preview': 'https://preview.daimaduan.com',
    'production': 'https://daimaduan.com'
}
NEWRELIC_APPLICATION_ID = {
    'preview': '13327736',
    'production': '13331097'
}


@task
def pack():
    """Create a new source distribution as tarball"""
    local('python setup.py sdist --formats=gztar', capture=False)


@task
def bootstrap(app_env):
    """Create bootstrap environment for daimaduan"""
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


@task
def deploy(app_env):
    """Deploy it to server"""
    if not app_env:
        print "fab pack deploy:<ENV>"
        sys.exit(1)

    with open('.newrelic_key') as f:
        newrelic_key = f.read().strip()
    if not newrelic_key:
        print "cannot find newrelic_key in .newrelic_key file"
        sys.exit(1)

    app_path = '/var/www/%s/%s' % (APP_NAME, app_env)
    out = run('ls -t %s | grep -v current | grep daimaduan.com' % app_path)
    versions = [i.strip() for i in out.split("\n")]
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '%s/%s.tar.gz' % (app_path, dist))
    with cd(app_path):
        run('tar xzf %s.tar.gz' % dist)
    with cd('%s/%s' % (app_path, dist)):
        run('%s/venv/bin/python setup.py develop > /dev/null 2>&1' % app_path)
    run('rm -f %s/current' % app_path)
    run('ln -s %s/%s/daimaduan %s/current' % (app_path, dist, app_path))
    run('cp %s/shared/config.cfg %s/current' % (app_path, app_path))
    run('cp %s/shared/deploy.py %s/current' % (app_path, app_path))
    run('mkdir -p %s/current/static/.webassets-cache' % app_path)
    run('chmod 777 %s/current/static/.webassets-cache' % app_path)
    run('chmod 777 %s/current/static/js/compiled.js' % app_path)

    # touching uwsgi ini file will reload this app
    sudo('touch /etc/uwsgi.d/daimaduan_%s.ini' % app_env)

    run('rm -f %s/%s.tar.gz' % (app_path, dist))

    # after deploying, we need to test if deployment succeed
    is_deploy_succeed = True
    try:
        resp = urllib2.urlopen(TEST_WEBSITE[app_env])
    except Exception:
        is_deploy_succeed = False
    else:
        if resp.code != 200:
            is_deploy_succeed = False
            if versions:
                print "Deploy failed, switch back to previous version"
                run('rm -f %s/current' % app_path)
                run('ln -s %s/%s/daimaduan %s/current' % (app_path, versions[0], app_path))
                sudo('touch /etc/uwsgi.d/daimaduan_%s.ini' % app_env)
                sys.exit(1)

    # clean old versions
    if is_deploy_succeed:
        versions.insert(0, dist)
    else:
        versions.append(dist)
    if len(versions) > 4:
        versions = ["%s/%s" % (app_path, i) for i in versions]
        versions_to_delete = " ".join(versions[3:])
        print versions_to_delete
        # run('rm -rf %s' % versions_to_delete)

    # send deployments notification to newrelic
    # version = local('python setup.py --version', capture=True).strip()
    # local('curl -H "x-api-key:%s" -d "deployment[application_id]=%s" '
    #       '-d "deployment[revision]=%s" -d "deployment[user]=David Xie" '
    #       'https://api.newrelic.com/deployments.xml' % (newrelic_key, NEWRELIC_APPLICATION_ID[app_env], version))
