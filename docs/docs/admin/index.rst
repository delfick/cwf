.. _admin_index:

Admin
=====

.. toctree::
    :hidden:

    buttons

CWF provides the ability to add buttons to your admin pages with relative ease.

As long as you have made the CWF templates
:ref:`available <template_availability>` and your admin class subclasses
``cwf.admin.ButtonAdmin``, then you can give your admin a list of buttons that
are rendered on your admin page and call particular functions on your admin
class when they are pressed.

How it works
------------

There are two things that are necessary to make extra buttons work on the admin:

    Modified urls for that admin
        Django admin classes have a ``urls`` function that is used to generate
        the urlpatterns for that particular admin.

        The ``cwf.admin.ButtonAdmin`` class overrides this function to add urls
        for each button that will figure out what function on the admin class
        to use when that url is requested.

    Display buttons to press
        ``cwf.admin.ButtonAdmin`` will add the buttons you put onto the class
        into the context when rendering the template for the changeform and the
        changelist views.

        Then, as long as the templates you are using are aware of these buttons,
        then they may be displayed.

Usage is something like:

.. code-block:: python

    from django.http import HttpResponse
    from django.contrib import admin

    from cwf.admin import ButtonAdmin, Button, ButtonGroup

    from webthing.models import AwesomeModel

    class AwesomeAdmin(ButtonAdmin):
        [..]

        buttons = (
              Button("one", "First")
            , Button("two", "Second")
            , ButtonGroup("Other",
                ( Button('three', "Third"
                    , description="The third button"
                    )
                , Button('four', "Fourth"
                    , description="The fourth button"
                    )
                )
            )

        def tool_one(self, request, ball, button):
            return HttpResponse("one")

        def tool_two(self, request, ball, button):
            return HttpResponse("two")

        def tool_three(self, request, ball, button):
            return HttpResponse("three")

        def tool_four(self, request, ball, button):
            return HttpResponse("four")

        [..]

    admin.site.register(AwesomeModel, AwesomeAdmin)

See :ref:`buttons` for what options are available.

.. _button_view:

Button View
-----------

When the admin urls are created, they create views that calls a function on the
admin that is found using the ``url`` of the button.

So if the ``url`` of the button is "one", then the view that is used for that
button will call ``tool_one`` on the admin class, passing in the request, the
object being edited and the instance of the button that was pressed.

This view may return a ``HttpResponse`` object directly
, or it may return a tuple of (File, extra)
, where ``File`` is the path to the template you want to render
and ``extra`` is any extra context that you want to provide to the template.

.. note:: The template will be rendered with a
  `RequestContext <https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.RequestContext>`_

You may also use the ``return_to_form`` :ref:`option <button_options>` to make
the view automatically redirect to the form where the button was pressed
regardless of what is returned from the ``tool_`` method.
