import pprint
from contextlib import contextmanager
import time
from fabric.context_managers import lcd, cd, prefix
from fabric.operations import local, sudo, run
from fabric.api import *


@contextmanager
def celery():
    ps = local('ps aux', capture=True)
    if not " -A settings worker" in ps:
        local(
            'cd backendfail && celery -A settings worker --loglevel=INFO &')  # this is
        #  probably really bad
        time.sleep(5)
    yield
    local('killall celery')  # this is probably really bad


@contextmanager
def conditional(condition, manager, *args):
    if condition:
        with manager(*args):
            yield
    else:
        yield


@contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


def dev():
    with celery(), rabbitmq():
        local(
            'cd backendfail && python manage.py migrate && python manage.py runserver '
            '0.0.0.0:8000')  # this is probably really bad


@contextmanager
def runserver():
    with lcd("backendfail"):
        local(r'python manage.py migrate')
        local(r'python manage.py runserver 0.0.0.0:9000 &')
        time.sleep(3)
    yield
    with lcd("backendfail"), suppress(SystemError):
        local(r'killall python')
        local(r'rm -f db.sqlite3')


def test_development():
    local(r'docker-compose -f etc/test_development.yml pull')
    local(r'docker-compose -f etc/test_development.yml up')


def coverage():
    o = ','.join(["backendfail/tests/**", "backendfail/settings/**,**/skeleton/**"])
    s = "backendfail"
    return r'coverage run --append --omit="' + o + '" --source ' + s + " -m "


def _test(*tags):
    local("rm -f .coverage")
    coverages = {}
    pytest_arguments = '-v backendfail/tests'
    with conditional('ui' in tags, runserver):
        for tag in tags:
            local(coverage() + r'py.test -m "' + tag + '" ' + pytest_arguments)
            partial_coverage = local("coverage report", capture=True)
            coverages[tag] = partial_coverage.split("\n")[-1]
            local("mv .coverage .coverage." + tag)
    local("coverage combine")
    for key, value in coverages.items():
        print '{:10s}{:s}'.format(key, value[10:].strip())


def test(*selectors):
    if selectors == ():
        selectors = ["unit", "integration", "system", "ui"]
    with conditional('ui' in selectors, selenium):
        _test(*selectors)


def test_ci_environment():
    _test("unit", "integration", "system", "ui")


# local(r'py.test -m "ui" -v backendfail/tests')


def graphite():
    local(
        r"docker run --name graphite -p 8005:80 -p 2003:2003 -p 8125:8125/udp -d "
        r"hopsoft/graphite-statsd")


@contextmanager
def selenium():
    image = "selenium/standalone-chrome"
    with settings(warn_only=True):
        local(r"docker rm -f selenium")
        local(r"docker run --net='host' --name selenium -d " + image)
        yield
        local(r"docker rm -f selenium")


@contextmanager
def rabbitmq():
    try:
        local(r"docker start rabbitmq")
        yield
        local(r"docker stop rabbitmq")
    except:
        local("docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq",
              capture=True)
        time.sleep(10)
        with rabbitmq():
            yield


def postgresql():
    try:
        sudo(
            r"docker run  --name postgresql -p 5432:5432 -e 'DB_USER=backendfail' -e "
            r"'DB_NAME=backendfail' -e 'DB_PASS=backendfail' -d sameersbn/postgresql")
    except:
        sudo(r"docker start postgresql")


def recruit(user):
    pubkey = local("cat ~/.ssh/id_rsa.pub", capture=True)
    try:
        if not pubkey in sudo("cat /home/" + user + "/.ssh/authorized_keys"):
            sudo("echo '" + pubkey + "' >> /home/" + user + "/.ssh/authorized_keys")
    except:
        sudo("echo '" + pubkey + "' >> /home/" + user + "/.ssh/authorized_keys")


def copy_secret(root="/var/www/bf"):
    secret = local("cat backendfail/settings/secret.py", capture=True)
    with cd(root + "/backendfail/settings"):
        run("echo '" + secret + "' > secret.py")


def init_git(destination='production'):
    sudo("apt-get install git")
    sudo("mkdir backendfail -p")
    sudo("chown -R backendfail /home/backendfail")
    with cd("backendfail"):
        run("git init --bare")
    try:
        local("git remote add " + destination + " backendfail@" + env.hosts[0].split("@")[
            1] + ":backendfail")
    except:
        pass
    with cd("backendfail/hooks"):
        postreceive = """'#!/bin/bash
git --work-tree=/var/www/bf/ checkout -f master
source /var/www/bf/env/bin/activate && cd /var/www/bf/ && pip install -r requirements.txt
source /var/www/bf/env/bin/activate && cd /var/www/bf/backendfail && python manage.py
migrate --settings=settings.production
source /var/www/bf/env/bin/activate && cd /var/www/bf/backendfail && python manage.py
collectstatic --noinput
source /var/www/bf/env/bin/activate && cd /var/www/bf/backendfail && bower install
sudo service supervisor restart
sudo nginx -s reload'"""
        run(" echo " + postreceive + " >post-receive")
        sudo("mkdir -p /var/www/bf")
        sudo("chown -R backendfail /var/www/bf")
        run(" chmod +x post-receive")

    local("git push " + destination + " master")


def create_users():
    sudo(" id -u gunicorn &>/dev/null || useradd gunicorn ")
    sudo(" id -u backendfail &>/dev/null || useradd backendfail ")
    sudo("adduser backendfail sudo")
    sudo("adduser backendfail docker")
    sudo("mkdir -p /home/backendfail/.ssh")
    sudo("echo \"ALL ALL=(ALL) NOPASSWD: ALL\" >> /etc/sudoers")
    recruit("backendfail")


def install_deploy_dependencies():
    sudo("apt-get -y install postgresql-server-dev-9.3 supervisor nginx memcached npm")
    try:
        sudo("ln -s /usr/bin/nodejs /usr/bin/node")
    except:
        pass
    sudo("npm install -g bower")
    sudo("pip install virtualenv")


def create_virtualenv(root='/var/www/bf'):
    with cd(root):
        try:
            run("virtualenv env")
        except:
            pass


def install_requirements(root='/var/www/bf'):
    with cd(root), prefix("source env/bin/activate"):
        run("pip install -r requirements.txt")
        run("pip install gunicorn psycopg2 python-memcached")
    with cd(root + "/backendfail"):
        run("bower install")


def symlink_config(root='/var/www/bf'):
    sudo("rm -f /etc/nginx/sites-enabled/default")
    sudo(
        "ln -sfn " + root + "/conf/supervisor.conf "
                            "/etc/supervisor/conf.d/backendfail.conf -f")
    sudo(
        "ln -sfn " + root + "/conf/nginx.conf /etc/nginx/sites-enabled/backendfail.conf "
                            "-f")


def management_commands(root='/var/www/bf'):
    with cd(root + "/backendfail"), prefix("source " + root + "/env/bin/activate"):
        run("python manage.py migrate --settings=settings.production")
        run("python manage.py collectstatic --noinput  --settings=settings.production")


def daemons():
    sudo('service supervisor restart')
    sudo('nginx -s reload')


def deploy(destination='production'):
    with settings(user="backendfail"):
        init_git(destination)
        install_deploy_dependencies()
        postgresql()
        rabbitmq()
        create_virtualenv()
        install_requirements()
        symlink_config()
        copy_secret()
        management_commands()
        daemons()


def clean():
    try:
        local("git remote rm production")
    except:
        pass
    try:
        local("rm -rf ~/backendfail/")
    except:
        pass


def tag_version(tag):
    from pipes import quote
    content = local("cat backendfail/templates/base.html", capture=True)
    content = quote(content.replace("VERSION", tag[:8]))
    local("echo " + content + " > backendfail/templates/base.html")


def deploy_staging():
    run("cd backendfail && docker-compose stop ")
    run("cd backendfail && docker-compose pull && docker-compose up -d")
