from fabric.context_managers import lcd, cd, prefix
from fabric.operations import local, sudo, run
from fabric.api import *


def test():
    with lcd('backendfail'):
        local('py.test django/test.py')


def ddocker(project='djangoname0'):
    with lcd("backendfail/media/djangoname0"):
        cmd = ["docker run"]
        cmd.append("--name " + project)
        cmd.append('-v "$PWD":/usr/src/app')
        cmd.append('-w /usr/src/app')
        cmd.append('-p 8000:8000')
        cmd.append('-d django')
        cmd.append('bash -c "python manage.py runserver 0.0.0.0:8000"')
        local(' '.join(cmd))


def test():
    return local(r'py.test -n 4 tests')


def coverage():
    local(
        r'coverage run --omit="backendfail/ror/**,backendfail/tests/**,backendfail/settings/**,**/skeleton/**" --source backendfail -m py.test backendfail/tests')


def graphite():
    local(r"docker run --name graphite -p 8005:80 -p 2003:2003 -p 8125:8125/udp -d hopsoft/graphite-statsd")


def selenium():
    local(r"docker run --name selenium -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome")


def rabbitmq():
    local("docker run -d -p 5672:5672 -p 15672:15672 rabbitmq")
def postgresql():
    try:
        sudo(
            r"docker run  --name postgresql -p 5432:5432 -e 'DB_USER=backendfail' -e 'DB_NAME=backendfail' -e 'DB_PASS=backendfail' -d sameersbn/postgresql")
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
        local("git remote add " + destination + " backendfail@" + env.hosts[0].split("@")[1] + ":backendfail")
    except:
        pass
    with cd("backendfail/hooks"):
        postreceive = """'#!/bin/bash
git --work-tree=/var/www/bf/ checkout -f master
source /var/www/bf/env/bin/activate && cd /var/www/bf/ && pip install -r requirements.txt
source /var/www/bf/env/bin/activate && cd /var/www/bf/backendfail && python manage.py migrate --settings=settings.production
source /var/www/bf/env/bin/activate && cd /var/www/bf/backendfail && python manage.py collectstatic --noinput
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
    sudo("ln -sfn " + root + "/conf/supervisor.conf /etc/supervisor/conf.d/backendfail.conf -f")
    sudo("ln -sfn " + root + "/conf/nginx.conf /etc/nginx/sites-enabled/backendfail.conf -f")


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
