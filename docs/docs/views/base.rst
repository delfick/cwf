.. _views_base:

Base View
=========

Django only requires a callable object to represent a view, which means you
either provide a function, or an instance of a class that implements the special
\_\_call\_\_ method.

Django provides it's own class based views where one class represents one view.

CWF class based views were created before this idea came around and does it a
little differently in that it represents a collection of views and which view
is used when the instance of the class is called is determined by the ``target``
parameter which is a string representing the name of the method to use.

This means you can use CWF view as follows:

.. code-block:: python
    
    # in webthing.somesection.views

    from cwf.views import View
    class MyAwesomeView(View):
        def thing(self, request):
            return "path/to/template.html", {}

To define the view and either the following with a 
:ref:`Section <sections_sections>`

.. code-block:: python

    # in webthing.somesection.urls

    from cwf.sections import Section

    section = Section('').configure(''
         , kls = "MyAwesomeView"
         , target = "thing"
         , module = 'webthings.somesection.views'
         )

    urlpatterns = section.patterns()

Or if you prefer a more manual approach to your urlpatterns:

.. code-block:: python

    # in webthing.somesection.urls

    from webthing.somesection.views import MyAwesomeView
    from django.conf.urls.defaults import *

    urlpatterns = patterns(''
        , ( '^$', MyAwesomeView(), {'target':'thing'})
        )

.. note:: You can create as many or as little instances of a View class as you
  wish as long as you don't put any state on the instance.

Calling a view
==============

When an instance of the view class is called, it will do the following:

    * Create :ref:`view state <views_view_state>`
    * :ref:`Clean kwargs <views_view_kwargs>`
    * Get a :ref:`result <views_view_result>` to render
    * :ref:`Render <views_view_rendering>` the result and return.

.. _views_view_state:

View State
==========

To assist with keeping state off the instance of the class, the call method of
the View will create a ``state`` object that is added to request.

This is a special object that behaves like a javascript object (supports both
dot notation and array notation for accessing and setting variables).

When it's created, it is initialized with some values:

    ``menu``
        If we got here via a CWF Section, then we will be able to create
        a Menu object from that section.

    ``path``
        The path of the request with no leading, trailing; or duplicate slashes.

    ``target``
        The target being reached on the class.

    ``section``
        The CWF section that is executing this view (if one was used)

    ``base_url``
        ``request.META.get('SCRIPT_NAME', '')``

.. _views_view_kwargs:

Cleaning View kwargs
====================

All keyword arguments to the view will be cleaned as according to the
``clean_view_kwarg`` method before being passed into the target.

By default this means any string keyword argument will be stripped of any
trailing slashes.

.. _views_view_result:

Getting result for a view
=========================

The view has a ``get_result`` method that takes the ``request`` object
, the ``target`` that is been called and any positional arguments and
:ref:`cleaned <views_view_kwargs>` keyword arguments and returns a result that
will be :ref:`rendered <views_view_rendering>`.

If the view has an ``override`` method, then it will pass all those arguments
in that function and return it's result.

Otherwise, it will check if that target exists using the ``has_target`` method,
which takes in the target and returns a ``True`` if the target exists or a
``False`` if the target doesn't exist.

If the target doesn't exist then an exception will be raised, otherwise it will
get the result from passing all the arguments into ``self.execute``.

If the result of ``self.execute`` is a callable then it will return the result
of calling this callable with the ``request`` object, otherwise it just returns
the result.

By default, the ``execute`` method will use ``self.get_target(target)`` to get
a callable for that target and call it with the ``request`` object and those
extra positional and keyword arguments.

By default, the ``get_target`` method just does a ``getattr`` on the instance.

.. _views_view_rendering:

Rendering a view
================

If the result being rendered is ``None``, then a ``Http404`` will be raised.

If the result is a list or tuple of two items, then it assumes this list
represents ``(template, extra)`` where ``template`` is the name of the template
to render and ``extra`` is any extra context to render the template with.

If ``template`` is None, then ``extra`` is returned, otherwise it uses the
:ref:`renderer object <views_rendering>` to render the template and context.

If the result to render is not a two item tuple or list, then it just returns
it as is.
