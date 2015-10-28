from fabric.context_managers import lcd
from fabric.operations import local

def test():
    with lcd('backendfiddle'):
        local('py.test django/test.py')
def ddocker(project='djangoname0'):
    with lcd("backendfiddle/media/djangoname0"):
        cmd = ["docker run"]
        cmd.append("--name "+project)
        cmd.append('-v "$PWD":/usr/src/app')
        cmd.append('-w /usr/src/app')
        cmd.append('-p 8000:8000')
        cmd.append('-d django')
        cmd.append('bash -c "python manage.py runserver 0.0.0.0:8000"')
        local(' '.join(cmd))

def test():
    return local(r'py.test -n 4 tests')
def coverage():
    local(r'coverage run --omit="backendfiddle/ror/**,backendfiddle/tests/**,backendfiddle/settings/**,**/skeleton/**" --source backendfiddle -m py.test backendfiddle/tests')
