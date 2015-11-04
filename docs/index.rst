backend.fail
============
Coding is **fun**, and learning to code should be **fun too**.


    **"If you're not failing every now and again, it's a sign you're not doing anything very innovative."**
    -- Woody Allen

    **"Failure is the first step to being sort of good at something"**
    -- Jake the dog

`backend.fail`_ is an interactive playground for backend development
that takes care of the boring parts, so beginners can learn online without frustration.

Motivation
----------
First Steps
###########
We have all experienced the **steep learning curve of web development**. Especially the first
steps with any given framework are confusing and demotivating. Every framework has its
dependencies, and those must be resolved by beginners before they can start learning
anything:

- Operating system (e.g.: **Windows**)
- Programming Language (e.g. : **Ruby**)
- Package management (e.g.: **Gems**, **Gemsets**, **pip**, **virtualenv**, **rvm**, ...)
- Command Line Interfaces (e.g.: **django-admin**)

When we are trying to make others passionate about programming, it is the most
important thing that they can see the results of their work *immediately*. Setting up
environments can be very demotivating.

-----

Reproducible Problems and Solutions
###################################
On the other hand, **explaining server side code** to beginners **is difficult**. [1]_ [2]_

For frontend development, web services like jsfiddle_ or codepen_ provide easily
accessible platforms to create a Minimal, Complete and Verifiable Example (MVCE_).

However even for experienced programmers it is difficult to write MVCEs for backend code.
There are many moving parts like databases, views, controllers and models which need to fit together.

When someone aks for help with their project online, the code provided by a them might be
incomplete or irrelevant to the problem they are experiencing, while answers provided by
experts remain unverifiable.

**backend.fail strives to these problems**

The Solution
------------
Containers
##########
`backend.fail`_ is able to run any web application in an isolated container.
A container consists of:

- Pre-installed dependencies and plugins.
- A **minimal set of files** as a starting point.
- A set of management commands such as `python manage.py runserver` to start the application.

In the main editor window, the preview displays the **result of a request** to an application
on the right side of the screen, while the left side features an **online code editor**.

When a user edits code, a new container is spawned with the new content, and the result will be different.

`backend.fail`_ is a great place to try out a tutorial or to answer a question with a code example.

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


.. toctree::
:maxdepth: 2

.. [1] `Question on Django`_
.. [2] `Question on Rails`_

.. _Question on Django: http://stackoverflow.com/questions/33342639/django-1-8-resultview-object-has-no-attribute-method
.. _Question on Rails: http://stackoverflow.com/questions/33527001/rails-questionnaires-app

.. _jsfiddle: https://jsfiddle.net/
.. _codepen: https://codepen.io/
.. _MVCE: http://stackoverflow.com/help/mcve
.. _backend.fail: https://backend.fail/


