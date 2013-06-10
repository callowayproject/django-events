"""
Provisioning an app server:

* Use the chef libraries to get the server ready
* fab -H <new server> deploy_updateable:<TAG TO DEPLOY>
* fab -H <new server> activate_tag:<TAG TO_DEPLOY>

"""
from fabric.api import cd, env, hosts, local, run, runs_once, sudo, prefix
from fabric.contrib.files import exists, sed, append
import os
import datetime

DEPLOY_ROOT = '/home/natgeo/sites/'
env.site_root = "%seducation/" % DEPLOY_ROOT
env.repo_url = "github.com:callowayproject/django-events.git"

TEST_HOST = "natgeo@67.43.4.153"
PROD_HOST = ["natgeo@67.43.4.34"]

if not 'site_root' in env:
    print "You must specify a path in the env.site_root variable."

if not 'repo_url' in env:
    print "You must specify the URL of the repository in the env.repo_url variable."


def _read_key_file(key_file):
    key_file = os.path.expanduser(key_file)

    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()


def push_key(key_file='~/.ssh/id_rsa.pub'):
    key_text = _read_key_file(key_file)
    if not exists('~/.ssh'):
        run('mkdir -p ~/.ssh && touch ~/.ssh/authorized_keys && chmod 700 ~/.ssh')
    append('~/.ssh/authorized_keys', key_text)


@hosts(TEST_HOST)
def make_test_instance(branchname, instance_name="events"):
    """
    Make a stand-alone instance with name of branchname on the test server
    """
    if not instance_name:
        instance_name = branchname
    instance_dir = env.site_root + instance_name
    if not exists(instance_dir):
        with cd(env.site_root):
            run('git clone %s %s' % (env.repo_url, instance_name))
        with cd(instance_dir):
            run('git checkout %s' % branchname)
    else:
        with cd(instance_dir):
            run("git pull")

    bootstrap(instance_name, 'test')

    upstart_conf_templ = os.path.join(instance_dir, 'example', 'conf', 'upstart-test.conf.template')
    upstart_conf = os.path.join(instance_dir, 'example', 'conf', 'upstart-test.conf')
    if not exists(upstart_conf):
        run('cp %s %s' % (upstart_conf_templ, upstart_conf))
        sed(upstart_conf, '\\{branchname\\}', instance_name)
    upstart_link = "/etc/init/%s.conf" % instance_name
    if not exists(upstart_link):
        sudo('ln -s %s %s' % (upstart_conf, upstart_link))
    sudo('initctl reload-configuration')
    sudo('start %s' % instance_name)

    apache_config_templ = os.path.join(instance_dir, 'example', 'conf', 'nginx-test.conf.template')
    apache_config = os.path.join(instance_dir, 'example', 'conf', 'nginx-test.conf')
    if not exists(apache_config):
        run('cp %s %s' % (apache_config_templ, apache_config))
        sed(apache_config, '\\{branchname\\}', instance_name)
    apache_name = '/etc/nginx/sites-available/%s' % instance_name
    if not exists(apache_name):
        sudo('ln -s %s %s' % (apache_config, apache_name))
        sudo('nxensite %s' % instance_name)
    sudo('mkdir -p %s%s/media/static' % (env.site_root, instance_name))
    sudo('chgrp -R www-data %s%s/media/static' % (env.site_root, instance_name))
    sudo('chmod -R g+w %s%s/media/static' % (env.site_root, instance_name))
    sudo('/etc/init.d/nginx reload')


@hosts(TEST_HOST)
def remove_test_instance(instance_name):
    """
    Remove a test instance and remove all support scripts and configs
    """
    nginx_name = '/etc/nginx/sites-enabled/%s' % instance_name
    if exists(nginx_name):
        sudo('nxdissite %s' % instance_name)
        sudo('/etc/init.d/nginx reload')
    nginx_name = '/etc/nginx/sites-available/%s' % instance_name
    if exists(nginx_name):
        sudo('rm %s' % nginx_name)

    upstart_link = "/etc/init/%s.conf" % instance_name
    if exists(upstart_link):
        sudo('stop %s' % instance_name)
        sudo('rm %s' % upstart_link)
        sudo('initctl reload-configuration')

    instance_dir = env.site_root + instance_name
    if exists(instance_dir):
        run('rm -Rf %s' % instance_dir)


@hosts(TEST_HOST)
def stop_test_instance(test_name=None):
    """
    Stop all the test instances
    """
    env.warn_only = True
    if test_name is not None:
        instances = [test_name]
    else:
        output = run('ls -1 %s' % env.site_root)
        instances = [x.strip() for x in output.split("\n")]
    for item in instances:
        sudo("stop %s" % item.strip())


@hosts(TEST_HOST)
def start_test_instance(test_name=None):
    """
    Stop all the test instances
    """
    env.warn_only = True
    if test_name is not None:
        instances = [test_name]
    else:
        output = run('ls -1 %s' % env.site_root)
        instances = [x.strip() for x in output.split("\n")]
    for item in instances:
        sudo("start %s" % item.strip())


@hosts(TEST_HOST)
def list_test_instances():
    """
    List all the test instances on the test server
    """
    run('ls -1 %s' % env.site_root)


@hosts(TEST_HOST)
def reload_test(test_name):
    """
    Reload the <test_name> deployment on the test server
    """
    sudo("restart %s" % test_name)


@hosts(TEST_HOST)
def update_test(test_name):
    """
    Update the <test_name> deployment on the test server
    """
    test_dir = env.site_root + test_name + '/example'
    with cd(test_dir):
        run("git pull")

        with prefix('source virtualenv/bin/activate'):
            run("pip install -r requirements.txt")
            run("./manage.py collectstatic --noinput --verbosity 0")
            run("./manage.py syncdb")
            # run("./manage.py migrate --delete-ghost-migrations --settings settings.test")
            reload_test(test_name)


@runs_once
def make_tag(tag):
    """
    Create a tag in the local repository and push it to origin
    """
    local('git tag %s;git push --tags' % tag)


def activate_tag(tag):
    """
    Activate the given tag
    """
    cur_deploy_link = "%scurrent_deploy" % env.site_root
    cur_deploy_path = "%s%s" % (env.site_root, tag)
    nginx_conf_link = "/etc/nginx/sites-available/education"
    nginx_conf_path = "%s/conf/nginx.conf" % cur_deploy_link
    upstart_link = "/etc/init/education"
    upstart_path = "%s/conf/upstart.conf" % cur_deploy_link
    run('rm -f %s' % cur_deploy_link)
    run('ln -s %s %s' % (cur_deploy_path, cur_deploy_link))
    sudo("[ ! -L %s ] && ln -s %s %s" % (nginx_conf_link, nginx_conf_path, nginx_conf_link))
    sudo("[ ! -L %s ] && ln -s %s %s" % (upstart_link, upstart_path, upstart_link))
    if not exists("/etc/nginx/sites-enabled/education"):
        sudo("nxensite education")
    sudo('restart education')


def bootstrap(tag, settings='production'):
    """
    Bootstrap a deployment. Useful if something fails, or if you just want to.
    """
    deploy_dir = "%s%s/example" % (env.site_root, tag)
    virtualenv = "%s/virtualenv" % deploy_dir

    # Bootstrap the code
    with cd(deploy_dir):
        run("python bootstrap.py")
        with prefix('source %s/bin/activate' % virtualenv):
            run("./manage.py collectstatic --noinput --verbosity 0 --settings settings.%s" % settings)
            run("./manage.py syncdb")
            # run("./manage.py migrate --delete-ghost-migrations")


def deploy_updateable(tag):
    """
    Deploy a checkout of the repository.
    """
    deploy_dir = "%s%s" % (env.site_root, tag)
    if exists(deploy_dir):
        print "%s is already deployed." % tag
        return
    with cd(env.site_root):
        run('git clone %s %s' % (env.repo_url, tag))
    with cd(deploy_dir):
        run('git checkout %s' % tag)
    bootstrap(tag)


@hosts(PROD_HOST)
def update(tag=None):
    """
    Update the current_deploy to tag
    """
    deploy_dir = "%scurrent_deploy" % env.site_root
    virtualenv = "%s/virtualenv" % deploy_dir
    if tag is None and not env.get('tag', False):
        tag = datetime.datetime.now().strftime("D%Y%m%d%H%M")
        env.tag = tag
        make_tag(tag)

    with cd(deploy_dir):
        run('git fetch --tags')
        run('git reset --hard HEAD')
        run('git checkout %s' % tag)

        with prefix('source %s/bin/activate' % virtualenv):
            run("pip install -r requirements.txt")
            run("./manage.py collectstatic --noinput --verbosity 0 --settings settings.production")
            run("./manage.py syncdb --settings settings.production")
            run("./manage.py migrate --delete-ghost-migrations --settings settings.production")
            run("./manage.py compress --settings settings.production --force -v 0")
            sudo("restart education")
