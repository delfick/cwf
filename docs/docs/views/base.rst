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

