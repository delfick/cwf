.. _views_base:

Base View
=========

.. currentmodule:: cwf.views.base

.. autoclass:: View

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

.. automethod:: View.__call__

.. _views_view_state:

View State
==========

Rather than keeping state on the View instance, CWF will use the ``get_state``
method to create an object that you can use to store state for the request.

The view will create this ``state`` object when the view is being called
and make it available from ``request.state``.

.. automethod:: View.get_state

.. _views_view_kwargs:

Cleaning View kwargs
====================

All keyword arguments to the view will be cleaned as according to the
``clean_view_kwarg`` method before being passed into the target.

.. automethod:: View.clean_view_kwargs

.. automethod:: View.clean_view_kwarg

.. _views_view_result:

Getting result for a view
=========================


.. automethod:: View.get_result

.. py:method:: View.override(request, target, args, kwargs)
    
    Not defined by default on the BaseView

    If implemented, then ``get_result`` will use this as a short circuit to
    skip the normal machinery

.. automethod:: View.execute

.. automethod:: View.has_target

.. automethod:: View.get_target

.. _views_view_rendering:

Rendering a view
================

.. automethod:: View.rendered_from_result
