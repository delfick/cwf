.. _sections_views:

Views for a url
===============

Included in the :ref:`options <section_configure>` you have available when you
are configuring your sections are some available for specifying what view
should be used for that section.

.. _section_configure_view:

Section view options
--------------------

We have options available for specifying whether to redirect to a url or
execute a particular view callable; as well as whether to bypass the view
altogether with access restriction.

You may also pass extra keyword arguments into the view that gets called via
the ``extra_context`` option.

.. _section_view_target:

Setting the view
++++++++++++++++

There are four options availbe to set what view should be invoked when a
particular section is accessed:

    ``redirect``
        Overwrites the other options and will mean the section redirects to this
        address. This can be a callable that takes in a request object.

        If the url specified doesn't begin with a slash, then it will be made
        relative to the ``request.path``.

        All duplicate slashes will be removed from the url before it is used
        for the redirect.

    ``target``
        If this is a callable object, then it is used as the view without any
        consideration of the other options.

        If it is a string, then the :ref:`dispatcher <section_dispatcher>` is
        used.

        If it is set to None, (and the section has no redirect)
        , then the section is considered to have no view

    ``kls`` and ``module``
        These are only considered if target is a string and all three values are
        used with the :ref:`dispatcher <section_dispatcher>`

.. note:: Sections that don't have a configured view won't appear in the
  generated ``urlpatterns``.

.. _section_dispatcher:

Section Dispatcher
++++++++++++++++++

CWF provides an object called the ``dispatcher`` that is used as the
view callable when the ``target`` is set as a string.

Django provides the ability to set a dictionary of options in the urlpatterns
that is passed into the view when it gets called. CWF uses this dictionary to
set the ``target`` and a ``kls`` values
(from combining the ``kls`` and ``module`` options) and the dispatcher will use
these two values to find the callable at request time.

It does this by creating (and caching) an instance of the ``kls`` value passed
into the dispatcher and then using "getattr(instance, target)" to get the view
to use.

This ``kls`` value is determined by looking at the ``kls`` and ``module``
options on the section.

If both are None, then no class can be determined.

If the ``kls`` is already an object then it is used and ``module`` is ignored.

If the ``kls`` is a string and the module is not defined
, then the string is sanitised
(leading and trailing dots are removed and invalid import names raise exceptions)

If module is a string, then it is sanitised and then concatenated with kls
(using a dot as a seperator) and returned.

If module is an object, then the parts of the kls are used with getattr to get
the view. So if ``kls`` option is "some.thing", the ``kls`` value will be found
from "getattr(getattr(module, 'some'), 'thing')".

.. _section_forced_404:

Forcing a 404 for a url
+++++++++++++++++++++++

If the ``exists`` or ``active`` options evaluate to ``False`` then that section
will return a 404 when it is accessed.

.. note:: These can be set to a callable that takes in the request object.

For example:

.. code-block:: python

    from cwf.sections import Section
    from datetime import date

    section = Section().configure(module="webthing.views")

    def only_at_christmas(request):
        """Conditional that only returns True if it's christmas"""
        today = date.today()
        return today.month == 12 and today.day == 25

    christmas = section.add('christmas'
        , target="christmas"
        , active=only_at_christmas
        )

    urlpatterns = section.patterns()

In this example, the "^christmas$" urlpattern always exists, but it will always
return a 404 unless it's christmas day
, where it will use the ``webthing.views.christmas`` view.

The ``exists`` option behaves exactly as the ``active`` option
, and there is only a logical difference between the two as determined by
you as the developer of the website.

.. _section_admin_only:

Admin only views
++++++++++++++++

You can specify that a view needs authorization to be accessed via the
``needs_auth`` option.

This can be set to either a boolean, string, list of strings or a callable that
takes in the request object.

If it set to a boolean or callable, then ``True`` means you can only access the
view if ``request.user.is_authenticated()`` evaluates to True.

If it is set to a string, then the user must be authenticated and have the
particular permission specified by the string.

If it is set to a list of strings, then the user must be authenticated and have
all the permissions specified.
