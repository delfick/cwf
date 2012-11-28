.. _templates_index:

Templates
=========

.. toctree::
    :hidden:

    menus
    admin

CWF comes with some templates you can use alongside some of the other features
that is provided.

Including Templates
-------------------

To be able to use these templates in your code, you need to make them available.

You either do this by adding the directory to CWF templates in your django
settings ``TEMPLATE_DIRS`` option or by adding a loader to the
``TEMPLATE_LOADERS`` option that understands where CWF is.

The first method could look something like this:

.. code-block:: python

    def __cwf_dirs__():
        """In a function so I don't pollute the settings namespace"""
        import pkg_resources
        cwf_templates = pkg_resources.resource_filename("cwf", "templates")
        return (cwf_templates, )

    TEMPLATE_DIRS = TEMPLATE_DIRS + __cwf_dirs__()

Alternatively, you could make a loader like this:

.. code-block:: python

    from django.template.loaders.app_directories import Loader
    from django.utils.importlib import import_module
    from django.utils._os import safe_join
    from django.conf import settings

    import sys
    import os

    class AppNameLoader(Loader):
        """Loader that will allow the app name in the template location"""
        @property
        def app_template_dirs(self):
            """Memoize the app template dirs"""
            if not hasattr(self, '_app_template_dirs'):
                self._app_template_dirs = tuple(self.get_app_template_dirs())
            return self._app_template_dirs

        def get_app_template_dirs(self):
            """Yield tuples of (app, template_dir) for each installed app"""
            fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
            for app in settings.INSTALLED_APPS:
                try:
                    mod = import_module(app)
                except ImportError, e:
                    raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))

                template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
                if os.path.isdir(template_dir):
                    yield app, template_dir.decode(fs_encoding)

        def get_template_sources(self, template_name, template_dirs=None):
            """Get template path relative to template dir of specified app"""
            base = template_name.split('/')[0]
            relpath = os.path.relpath(template_name, base)

            for app, template_dir in self.app_template_dirs:
                if app == base:
                    try:
                        yield safe_join(template_dir, relpath)
                    except UnicodeDecodeError:
                        # The template dir name was a bytestring that wasn't valid UTF-8.
                        raise
                    except ValueError:
                        # The joined path was located outside of template_dir.
                        pass

And add it to your template loaders:

.. code-block:: python

    TEMPLATE_LOADERS = TEMPLATE_LOADERS + 'path.to.AppNameLoader'

Which would mean that if 'cwf/menu/base.html' doesn't match for any of the other
template loaders you have, then it will take the first part of that url
(in this case, 'cwf') and find the template dir for that app and look in there.

Available Templates
-------------------

Templates are provided for the following:

    :doc:`admin`
        Templates for adding buttons to the admin pages.

    :doc:`menus`
        Templates for displaying :ref:`sections_menus`.
