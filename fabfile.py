from fabric.context_managers import lcd, cd, prefix
from fabric.operations import local, sudo, run


from fabric.api import *

def test():
    with lcd('backendfiddle'):
        local('py.test django/test.py')


def ddocker(project='djangoname0'):
    with lcd("backendfiddle/media/djangoname0"):
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
        r'coverage run --omit="backendfiddle/ror/**,backendfiddle/tests/**,backendfiddle/settings/**,**/skeleton/**" --source backendfiddle -m py.test backendfiddle/tests')


def graphite():
    local(r"docker run --name graphite -p 8005:80 -p 2003:2003 -p 8125:8125/udp -d hopsoft/graphite-statsd")


def selenium():
    local(r"docker run --name selenium -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome")


def postgresql():
    try:
        sudo(r"docker run  --name postgresql -p 5432:5432 -e 'DB_USER=backendfiddle' -e 'DB_NAME=backendfiddle' -e 'DB_PASS=backendfiddle' -d sameersbn/postgresql")
    except:
        sudo(r"docker start postgresql")




# def recruit(user=env.hosts[0].split("@")[0]):
#     pubkey=local("cat ~/.ssh/id_rsa.pub",capture=True)
#     if not pubkey in sudo("cat /home/"+user+"/.ssh/authorized_keys"):
#         sudo("echo '"+pubkey+"' >> /home/"+user+"/.ssh/authorized_keys")
def copy_secret(root="/var/www/bf"):
    secret = local("cat backendfiddle/settings/secret.py",capture=True)
    with cd(root+"/backendfiddle/settings"):
        run("echo '"+secret+"' > secret.py")
def init_git():
    sudo("apt-get install git")
    sudo("mkdir backendfiddle -p")
    sudo("chown -R backendfiddle /home/backendfiddle")
    with cd("backendfiddle"):
        run("git init --bare")
    try:
        local("git remote add production backendfiddle@" + env.hosts[0].split("@")[1] + ":backendfiddle")
    except:
        pass
    with cd("backendfiddle/hooks"):
        postreceive = """'#!/bin/bash
        git --work-tree=/var/www/bf/ checkout -f master'"""
        run(" echo " + postreceive + " >post-receive")
        sudo("mkdir -p /var/www/bf")
        sudo("chown -R backendfiddle /var/www/bf")
        run(" chmod +x post-receive")

    local("git push production master")


def create_users():
    sudo(" id -u gunicorn &>/dev/null || useradd gunicorn ")
    sudo(" id -u backendfiddle &>/dev/null || useradd backendfiddle ")
    sudo("adduser backendfiddle sudo")
    sudo("adduser backendfiddle docker")
    sudo("mkdir -p /home/backendfiddle/.ssh")
    sudo("echo \"ALL ALL=(ALL) NOPASSWD: ALL\" >> /etc/sudoers")
    recruit("backendfiddle")


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
    with cd(root+"/backendfiddle"):
        run("bower install")


def symlink_config(root='/var/www/bf'):
    sudo("rm -f /etc/nginx/sites-enabled/default")
    sudo("ln -sfn " + root + "/conf/supervisor.conf /etc/supervisor/conf.d/backendfiddle.conf -f")
    sudo("ln -sfn " + root + "/conf/nginx.conf /etc/nginx/sites-enabled/backendfiddle.conf -f")


def management_commands(root='/var/www/bf'):
    with cd(root+"/backendfiddle"), prefix("source "+root+"/env/bin/activate"):
        run("python manage.py migrate --settings=settings.production")
        run("python manage.py collectstatic --noinput  --settings=settings.production")


def daemons():
    sudo('service supervisor restart')
    sudo('nginx -s reload')


def deploy():
    with settings(user="backendfiddle"):
        init_git()
        install_deploy_dependencies()
        postgresql()
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
        local("rm -rf ~/backendfiddle/")
    except:
        pass


