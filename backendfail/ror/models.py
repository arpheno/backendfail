import os

from fiddles.models import Fiddle
from settings.basic import BASE_DIR


class RailsFiddle(Fiddle):
    @property
    def internal_port(self):
        return "3000"

    @property
    def startup_command(self):
        return ""

    @property
    def docker_image(self):
        return "arpheno/rails-skeleton"

    @property
    def entrypoint(self):
        return "README.rdoc"

    @property
    def prefix(self):
        return os.path.join(BASE_DIR, "ror", "skeleton/")
