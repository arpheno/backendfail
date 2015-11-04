.. image:: https://circleci.com/gh/arpheno/backendfail.svg?style=svg
:target: https://circleci.com/gh/arpheno/backendfail
    
.. image:: https://coveralls.io/repos/arpheno/backendfail/badge.svg?branch=master&service=github 
:target: https://coveralls.io/github/arpheno/backendfail?branch=master
    
.. image:: https://readthedocs.org/projects/backendfail/badge/?version=latest
:target: http://backendfail.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

backend.fail
============
Coding is **fun**, and learning to code should be **fun too**.


    **"If you're not failing every now and again, it's a sign you're not doing anything very innovative."**
    -- Woody Allen

    **"Failure is the first step to being sort of good at something"**
    -- Jake the dog

`backend.fail`_ is an interactive playground for backend development
that takes care of the boring parts, so beginners can learn online without frustration.

Documentation is available at readthedocs_

.. _readthedocs: http://backendfail.readthedocs.org/en/latest/

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

.. _backend.fail: https://backend.fail/
.. _docker hub:  https://hub.docker.com/
.. _django: http://djangoproject.org/
.. _rails: http://rubyonrails.org/


