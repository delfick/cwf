.. _splitter_website:

Website declaration
===================

Django doesn't provide any facilities out of the box for splitting up your
website into distinct parts with their own urls, views, admin and models.

Instead you must manually import these things in the ``package.views``
, ``package.admin``, ``package.views`` and ``package.models`` of your project
if it is best for your website to be split up this way.

CWF provides under ``cwf.splitter.website`` and ``cwf.splitter.parts`` classes
that provide the wiring that allows you to define your website with a folder per
part of the site and declaritevely wire them all together into one site.

So, assuming your project is structured as::

    webthings_main/
        __init__.py
        index/
            __init__.py
            urls.py
            views.py
        news/
            __init__.py
            models.py
            urls.py
            views.py
        events/
            __init__.py
            models.py
            urls.py
            views.py
        photos/
            __init__.py
            models.py
            urls.py
            views.py

You can create a ``Website`` representing these different parts:

.. code-block:: python

    from cwf.splitter.website import Website
    from cwf.splitter.parts import Part

    website = Website('webthings_main'
          , Part('index', first=True)
          , Part('news')
          , Part('events')
          , Part('photos')
          )

The website object takes in the package where all the parts are defined as
importable modules - ``webthings_main`` in this case; and ``Part`` objects
for the parts of the website we want to include.

The ``Part`` object holds the name of the part to import and any kwargs that are
eventually used when the part is used as a :ref:`section <section_children>`.

.. note:: The ``Part`` object also takes in an ``active`` keyword, which
  defaults to True. The ``Website`` object will use this to determine which
  parts should have its ``urls`` added to the website.

  The ``models`` and ``admin`` of a section will be imported regardless of the
  value of the ``active`` property.

This object will know how to import the section (part.do_import)
and load urls, admin and models from it (part.load('urls'), etc).

The website object will create a ``Parts`` object that will hold the collection
of ``Part`` objects provided.

The Parts collection has three main responsibilities:

        ``parts.load_admin()``
            Import ``part.admin`` for all the parts that have an ``admin.py``
            so that any django admin registration logic may be fired.

        ``parts.models()``
            Load all the ``part.models`` for all the parts that have
            ``models.py`` and return a dictionary of all {name:model} for all
            the models it finds.

            .. note:: For this to work, each ``models.py`` must define a
              ``__all__`` variable with either the names of the models as
              strings or the model objects themselves.

              Also, each model must have ``Meta.app_label`` set to the same
              package you provided to the ``Website``.

        ``parts.urls``
            Create a :ref:`Section <sections_sections>` object and add the
            ``section`` from each ``part.urls`` as
            :ref:`children <section_children>` to root section.

            It will then return {'site':site, 'urlpatterns':site.patterns()}
            where ``site`` is the root ``Section`` it just created.

            .. _section_include:

            .. note:: These sections will be added to the urlpatterns using the
              Django `include <https://docs.djangoproject.com/en/dev/ref/urls/#django.conf.urls.include>`_
              function.

Website will use this functionality to import the admin logic,
:ref:`inject <splitter_inject>` the ``models`` into ``package.models`` and
:ref:`inject <splitter_inject>` the ``site`` and ``urlpatterns`` into
``package.urls``.
