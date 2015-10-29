# Create your models here.
from fiddles.models import Fiddle
from settings.basic import BASE_DIR
import os


class DjangoFiddle(Fiddle):
    @property
    def internal_port(self):
        return "8000"

    @property
    def startup_command(self):
        return r"python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

    @property
    def docker_image(self):
        return "arpheno/rails-skeleton"

    @property
    def entrypoint(self):
        return "app/templates/app/app.html"

    @property
    def prefix(self):
        return os.path.join(BASE_DIR, "dj", "skeleton/")
