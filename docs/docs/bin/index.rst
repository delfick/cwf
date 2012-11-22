.. _bin_index:

Binaries
========

CWF comes with two command line applications that you can use to interact with
your Django project:

    :ref:`bin-cwf-manager`
        manage.py without creating the manage.py

    :ref:`bin-cwf-debugger`
        Start your django project using werkzeug and it's awesome debugger.

.. _bin-cwf-manager:

cwf-manager
-----------

The prescribed setup for a django project suggests creating a manage.py file
that is used to access all of django's nice manager functionality from the cli.

``cwf-manager`` implements the code that should go into manage.py such that
as long as you're in a folder with the same name as your project and you
have your project on your python path, then it will be able to access the
django admin functionality.

For example, say your project is called ``webthing`` and the settings.py can be
accessed via ``webthing.settings`` and your in a folder with the name
``webthing``, then::

    $ cwf-manager
        Usage: cwf-manager subcommand [options] [args]

        Options:
          -v VERBOSITY, --verbosity=VERBOSITY
                                Verbosity level; 0=minimal output, 1=normal output,
                                2=verbose output, 3=very verbose output
          --settings=SETTINGS   The Python path to a settings module, e.g.
                                "myproject.settings.main". If this isn't provided, the
                                DJANGO_SETTINGS_MODULE environment variable will be
                                used.
          --pythonpath=PYTHONPATH
                                A directory to add to the Python path, e.g.
                                "/home/djangoprojects/myproject".
          --traceback           Print traceback on exception
          --version             show program's version number and exit
          -h, --help            show this help message and exit

        Type 'cwf-manager help <subcommand>' for help on a specific subcommand.

        Available subcommands:

        [auth]
            changepassword
            createsuperuser

        [django]
            cleanup
            compilemessages
            createcachetable
            dbshell
            diffsettings
            dumpdata
            flush
            inspectdb
            loaddata
            makemessages
            reset
            runfcgi

    [etc]

.. _project_setup:

Project Setup
+++++++++++++

As an added bonus, you can do any project setup you wish before the manager
starts up by implementing ``webthing.project_setup`` as a callable that only
takes keyword arguments.

This ``project_setup`` function is called after the ``DJANGO_SETTINGS_MODULE``
environment variable is set, and before the django ``execute_from_command_line``
(the heart of manage.py) is called.

The return of ``project_setup`` is ignored.

.. _bin-cwf-debugger:

cwf-debugger
------------

Whilst ":ref:`bin-cwf-manager` runserver" provides a fine local server you can
develop with; it is nice to have werkzeug's
`awesome debugger <http://werkzeug.pocoo.org/docs/debug/>`_ and ``cwf-debugger``
makes that easy.

The first argument is the import path to your project. So as is for the
`bin-cwf-manager`, if your settings.py can be found under ``webthings.settings``
and you want to run a debug server of ``webthings``, you would use:

.. code-block:: bash

    $ cwf-debugger webthings

The debuggger has the same :ref:`project_setup <project_setup>` semantics as
:ref:`bin-cwf-manager` and also provides a ``-o`` flag
which you may use to pass in a json formatted string
that is used as keyword arguments to ``project_setup``.

.. note:: Unfortunately, the current implementation of cwf-debugger does require
  a small change to werkzeug : https://github.com/mitsuhiko/werkzeug/issues/220
