import ConfigParser
import sys
import urllib2
from datetime import datetime

from fabric.context_managers import cd
from fabric.decorators import task
from fabric.operations import local
from fabric.operations import put
from fabric.operations import run
from fabric.operations import sudo
from fabric.state import env

import upyun


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
    local('bower install')
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

    config = ConfigParser.ConfigParser()
    try:
        config.read('.upyun')
        upyun_bucket = config.get('upyun', 'bucket')
        upyun_username = config.get('upyun', 'username')
        upyun_password = config.get('upyun', 'password')
    except:
        print "cannot find .upyun file or .upyun is not correct"
        sys.exit(1)

    app_path, dist, versions = update_code_on_server(app_env)

    # after deploying, we need to test if deployment succeed
    is_deploy_succeed = True
    try:
        resp = urllib2.urlopen(TEST_WEBSITE[app_env])
        upload_files_to_upyun(app_env, upyun_bucket, upyun_password, upyun_username)
    except Exception as e:
        is_deploy_succeed = False
        print e
    else:
        if resp.code != 200:
            is_deploy_succeed = False
            if versions:
                print "Deploy failed, switch back to previous version"
                run('rm -f %s/current' % app_path)
                run('ln -s %s/%s/daimaduan %s/current' % (app_path, versions[0], app_path))
                sudo('touch /etc/uwsgi.d/daimaduan_%s.ini' % app_env)
                sys.exit(1)

    clean_old_versions(app_path, dist, is_deploy_succeed, versions)

    # send deployments notification to newrelic
    version = local('python setup.py --version', capture=True).strip()
    local('curl -H "x-api-key:%s" -d "deployment[application_id]=%s" '
          '-d "deployment[revision]=%s" -d "deployment[user]=David Xie" '
          'https://api.newrelic.com/deployments.xml' % (newrelic_key, NEWRELIC_APPLICATION_ID[app_env], version))


def clean_old_versions(app_path, dist, is_deploy_succeed, versions):
    # clean old versions
    if is_deploy_succeed:
        versions.insert(0, dist)
    else:
        versions.append(dist)
    if len(versions) > 4:
        versions = ["%s/%s" % (app_path, i) for i in versions]
        versions_to_delete = " ".join(versions[3:])
        run('rm -rf %s' % versions_to_delete)


def update_code_on_server(app_env):
    app_path = '/var/www/%s/%s' % (APP_NAME, app_env)
    out = run('ls -t %s | grep -v current | grep daimaduan.com' % app_path)
    versions = [i.strip() for i in out.split("\n")]
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    version = local('python setup.py --version', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '%s/%s.tar.gz' % (app_path, dist))
    with cd(app_path):
        run('tar xzf %s.tar.gz' % dist)
    with cd('%s/%s' % (app_path, dist)):
        run('%s/venv/bin/python setup.py develop > /dev/null 2>&1' % app_path)
    run('rm -f %s/current' % app_path)
    run('ln -s %s/%s/daimaduan %s/current' % (app_path, dist, app_path))
    run('cp %s/shared/custom_settings.py %s/current' % (app_path, app_path))
    run('sed "s/VERSION.*/VERSION = \'%s\'/" -i %s/current/custom_settings.py' % (version, app_path))
    run('sed "s/DEPLOYED_AT.*/DEPLOYED_AT = \'%s\'/" -i %s/current/custom_settings.py' % (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), app_path))
    run('cp %s/shared/deploy.py %s/current' % (app_path, app_path))
    # touching uwsgi ini file will reload this app
    sudo('touch /etc/uwsgi.d/daimaduan_%s.ini' % app_env)
    run('rm -f %s/%s.tar.gz' % (app_path, dist))
    return app_path, dist, versions


def upload_files_to_upyun(app_env, upyun_bucket, upyun_password, upyun_username):
    up = upyun.UpYun(upyun_bucket, username=upyun_username, password=upyun_password)
    prefix = ''
    if app_env == 'preview':
        prefix = '/preview'
    for i in ['static/css/compiled.css',
              'static/css/embed.css',
              'static/js/compiled.js']:
        with open("daimaduan/%s" % i, 'rb') as f:
            print "Uploading %s to upyun" % i
            up.put('%s/%s' % (prefix, i), f, checksum=True)
