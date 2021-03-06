Contributing
------------
Writing a plugin for a framework
________________________________
To run user applications written in a framework `backend.fail`_ needs a container template.
Container templates implement the boilerplate on which users can build their applications.

Currently the plugins for rails_ and django_ are implemented.

The steps to write a container template:
########################################

#. Find a suitable base image for the framework on `docker hub`_.
#. *(optional) modify base image if necessary.*
#. Create a folder ``backenfail/[framework]/``
#. Create a **minimal set of files** which does something useful in ``backenfail/[framework]/skeleton/``
#. Extend ``fiddles.models.Fiddle`` and add 5 properties ( example taken from the ``dj`` plugin):

    .. code-block:: python

        from fiddles.models import Fiddle
        class DjangoFiddle(Fiddle):
            @property
            def internal_port(self):
                """ This property specifies the port the framework is listening on inside the
                container."""
                return "8000"

            @property
            def startup_command(self):
                """ This property specifies a command that should be executed by the container on
                the commandline when it starts up."""
                return r"bash -c 'python manage.py makemigrations &&" \
                       r" python manage.py migrate && python manage.py runserver 0.0.0.0:8000'"

            @property
            def docker_image(self):
                """ This property specifies an image from the docker hub that should be run.
                It should expect the user sources under /usr/src/app/"""
                return "django"

            @property
            def entrypoint(self):
                """ This property defines the path to the file that a user should
                see in the editor when they create a new fiddle."""
                return "app/templates/app/app.html"

            @property
            def prefix(self):
                """ This property defines where the project skeleton is located. """
                return os.path.join(BASE_DIR, "dj", "skeleton/")

