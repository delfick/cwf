.. _splitter_index:

Splitter
========

.. toctree::
    :hidden:

    imports
    website

CWF provides the ability to seperate your website into multiple sections that
you can then stitch together.

The following is provided to allow for this:

    :ref:`Import modifiers <splitter_imports>`
        Functions to help with injecting values into and stealing values from
        import paths.

    :ref:`Website declaration <splitter_website>`
        Classes that let you specify what makes up your website.

Creating a website
------------------

Below is a slightly stripped down version of the how I setup the website
that was the inspiration for CWF.

At it's core you have ``webthings`` and ``webthings_main`` in your import path
where ``webthings_main`` knows about each part of your website
, and ``webthings`` knows how to combine together the parts of
``webthings_main`` and what settings to set for the website to work.

So, given the following structure::

    # Where the logic of the site actually goes.
    # each urls.py here uses CWF Section logic
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
        utils/
            template_loaders.py
        templates/
            errors/
                404.html
                500.html

    # All the configuration for the website is in a seperate module
    webthings/
        __init__.py
        config/
            __init__.py
            common/
                __init__.py
                settings.py
                site.py
                urls.py
            settings/
                __init__.py
                inclusions.py
                logging.py
                testing.py
                other.py
        wsgi/
            prod.py

.. note:: For cwf to be able to put all your models under the
    ``webthings_main.models`` namespace, all your models must have
    ``Meta.app_label`` set:

    .. code-block:: python

        from django.db import models

        class AwesomeModel(models.Model):
            [..]

            class Meta:
                app_label = 'webthings_main'

    And each ``__models__.py`` must have ``__all__`` explicitly set to all the
    models contained within:

    .. code-block:: python

        __all__ = [AwesomeModel]

``webthings.__init__``

.. code-block:: python

    from cwf.splitter.imports import install_failed_import_handler
    import sys
    import os

    def project_setup():
        # Install failed import handler
        install_failed_import_handler()

        # Setup the site
        from webthings.config.common import site

``webthings.config.common.site``

.. code-block:: python

    from cwf.splitter.website import Website
    from cwf.splitter.parts import Part as P
    from cwf.splitter.imports import inject
    from cwf.sections import Section

    import os

    ########################
    ###   SETTINGS
    ########################

    from webthings.config.common import settings

    class theSite(object):
        site = Section("", name='webthings').configure(''
          , promote_children=True
          )

        js = Section("", name='js').configure(''
            , alias   = 'js'
            , display = False
            , module  = None
            , kls     = None
            )

    # Create webthings.settings
    settings.THESITE = theSite
    inject(settings, 'webthings.settings')

    ########################
    ###   ACTIVE
    ########################

    # Create the website object to specify each part of the website
    website = Website(settings, 'webthings_main'
          , P('index', first=True)
          , P('news')
          , P('events')
          , P('photos')
          )

    # And configure the website
    website.configure()

    # Just make sure we can get the urls
    # Note we also have webthings_main.models available now
    # Because website.configure gives us webthings_main.urls and webthings_main.models
    from webthings_main.urls import site

    ########################
    ###   URLS
    ########################

    # Create urls
    # Depends on webthings being setup
    # Note that settings.ROOT_URLCONF is set to 'urls'
    from webthings.config.common import urls
    inject(urls, 'urls')

``webthings.config.common.settings``

.. code-block:: python

    from cwf.splitter.imports import steal, inject
    import os

    ########################
    ###   INJECTION
    ########################

    this_dir = os.path.dirname(__file__)
    settings_dir = os.path.abspath(os.path.join(this_dir, '..', 'settings'))
    steal('inclusions', 'logging', 'testing', 'other'
        , folder=settings_dir, globals=globals(), locals=locals()
      )

    if DEBUG:
        LOGGING['loggers']['']['level'] = 'DEBUG'

    ########################
    ###   INSTALLED
    ########################

    INSTALLED_APPS += (
          'webthings_main'
        , 'cwf'

        , 'grappelli'
        , 'django.contrib.admin'
        , 'django.contrib.sessions'

        , 'south'
        )

    ########################
    ###   TEMPLATES
    ########################

    def __get_template_dirs__():
        """In a function so I don't pollute the settings namespace"""
        import pkg_resources
        webthings_main_folder = pkg_resources.resource_filename("webthings_main", "")
        error_page_templates = pkg_resources.resource_filename("webthings_main", 'templates/errors')
        return (webthings_main_folder, error_page_templates, )

    TEMPLATE_DIRS = __get_template_dirs__()

    # Use the AppNameLoader as suggested in the templates section of the docs
    # To make it so cwf templates are available
    TEMPLATE_LOADERS = (
        'webthings_main.utils.template_loaders.AppNameLoader'
      ,
      )

    ROOT_URLCONF = 'urls'

``webthings.config.common.urls``

.. code-block:: python

    from django.conf.urls.defaults import patterns, include
    from django.contrib import admin
    from django.conf import settings

    ########################
    ###   GRAPPELLI
    ########################

    haveAdmin = 'django.contrib.admin' in settings.INSTALLED_APPS
    if haveAdmin:
        admin.autodiscover()

    ########################
    ###   CWF GENERATED URLS
    ########################

    theSite = settings.THESITE
    site = theSite.site

    from webthings_main.urls import site as main_site
    site.merge(main_site, take_base=True)

    if hasattr(theSite, 'js'):
        js = theSite.js
        site.adopt(js, consider_for_menu=False, include_as = 'js')

    urlpatterns = site.patterns()

    ########################
    ###   ADMIN URLS
    ########################

    if haveAdmin:
        urlpatterns += patterns('', (r'^grappelli/',  include('grappelli.urls')))
        urlpatterns += patterns('', (r'^admin/',      include(admin.site.urls)))

``webthings.wsgi.prod``

.. code-block:: python

    import webthings
    import sys
    import os

    def serve_site(production=True, internet=True):
        """
            Ensure we have DJANGO_SETTINGS_MODULE environment variable
            And return wsgi application for django
        """
        os.umask(2)

        # Setup project and set django_settings_module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'webthings.settings'
        webthings.project_setup()

        # Create and return wsgi app for django
        import django.core.handlers.wsgi
        return django.core.handlers.wsgi.WSGIHandler()

    application = serve_site()

You can then have a uwsgi configuration that looks like::

    [uwsgi]
    chdir=/path/to/webthings/wsgi
    module=prod:application
    vacuum=True
    home=/path/to/venv_for_webthings
    uid=www-data
    gid=www-data
    disable-logging=true
    touch-reload=/path/to/webthings/wsgi/prod.py

And an nginx configuration that looks like::

    server {
        server_name webthings;

        upstream webthings {
            ip_hash;
            server unix:///run/uwsgi/app/webthings/socket;
        }

        location / {
            include     uwsgi_params;
            uwsgi_pass  webthings;
        }
    }
