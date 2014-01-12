CWF
===

A layer of random utility that sits between Django and your site.

Mainly used so that you can specify what views go to what urls in such a way
that we can render a menu system from the same specification.

It also includes utilities to be able to seperate your site into multiple
folders within the same project, each including their own views, urls, models
and admin code.

Along with some other random helpers to make life with Django even simpler
than it already is.

Documentation can be found on readthedocs: https://cwf.readthedocs.org

Install from pypi::

    pip install cwf

Changelog
---------

    1.1.1 - 12th January 2014
        - Make cwf-debugger tell you about https://github.com/mitsuhiko/werkzeug/issues/220

    1.1 - 26th October 2013
        - Updated noseOfYeti
        - cwf-debugger now doesn't fail on projects without a project_setup
        - Update to work with newer Django
        - Minor typo

    1.0 - 13th January 2013
        - First public release after many years and a complete rewrite

