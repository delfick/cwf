.. _splitter_imports:

Import helpers
==============

There are three helpers under ``cwf.splitter.imports`` that you can use:

    :ref:`cwf.splitter.imports.steal <splitter_steal>`
        This lets you inject variables from several files into your current
        file without relying on magic "from somewhere import \*".

    :ref:`cwf.splitter.imports.inject <splitter_inject>`
        This lets you inject some object into import space.

    :ref:`cwf.splitter.imports.install_failed_import_handler <splitter_import_handler>`
        This provides a wrapper around the default __import__ logic that makes
        autoreload logic for development servers reload modules that never
        import properly.

.. _splitter_steal:

steal
-----

A django settings file tends to get very large and a bit unweildy.

You can use this to split your ``settings.py`` into many files that you combine
together.

For example, let's say you have the following folder structure::

    settings.py
    settings_files/
        inclusions.py
        logging.py
        cache.py
        other.py

Then you can have the following in your ``settings.py``:

.. code-block:: python

    from cwf.splitter.imports import steal

    this_dir = os.path.dirname(__file__)
    settings_dir = os.path.abspath(os.path.join(this_dir, 'settings_files'))
    steal('inclusions', 'logging', 'cache', 'other'
        , folder=settings_dir, globals=globals(), locals=locals()
        )

``steal`` will use `execfile <http://docs.python.org/2/library/functions.html#execfile>`_
to insert the variables from those files into the ``globals`` and ``locals``
that your provide.

.. _splitter_inject:

inject
------

Inject is a special beast that will create a
`finder <http://docs.python.org/2/glossary.html#term-finder>`_ object
that gets placed into
`sys.meta_path <http://docs.python.org/2/library/sys.html#sys.meta_path>`_

What this means is that you can write something like:

.. code-block:: python

    from cwf.splitter.imports import inject

    try:
        import blah
        assert False, "Blah shouldn't exist"
    except ImportError:
        assert True

    obj = {"one":1, "two":2}
    inject(obj, "blah")

    try:
        import blah
        assert blah.one == 1
        assert blah.two == 2
        print "successfully injected blah"
    except ImportError:
        assert False, "Blah should have been injected"

.. note:: There is a limitation to this in that all packages leading up your new
 import path must already exist and be folders.

 So if you inject into "blah.things", then "blah" must already exist in your
 PYTHONPATH and be a folder with an ``__init__.py`` for this to work.

.. _splitter_import_handler:

install_failed_import_handler
-----------------------------

When you start a development server that auto reloads for you (for example, the
werkzeug powered one :ref:`provided <bin-cwf-debugger>` then files will only be
reloaded if they are inside ``sys.modules``.

It so happens that if a module fails to import, then it won't end up in
``sys.modules`` and so when you edit such a file to not fail on import, the
reloader won't see that it has changed and ignore it.

To get around this, CWF provides
``cwf.splitter.imports.install_failed_import_handler``
that will wrap the default ``__import__`` such that any module that fails to
import will get a fake module put into ``sys.modules`` in it's place so that
the reloader knows to check that file.

Installation is as simple as:

.. code-block:: python

    from cwf.splitter.imports import install_failed_import_handler
    install_failed_import_handler()

It will consider either a ``SyntaxError`` or ``ImportError`` as conditions for
when a fake version of it should go into ``sys.modules``. Regardless of what
exception is raised, if any, it will always be reraised so that you are aware
when this happens.
