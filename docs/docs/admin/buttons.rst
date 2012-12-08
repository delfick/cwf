.. _buttons:

Buttons
=======

You can create buttons using ``cwf.admin.Button`` and ``cwf.admin.ButtonGroup``
classes where a ``ButtonGroup`` is merely a container of multiple ``Button``.

A ``ButtonGroup`` takes in a ``name`` and an iterable of ``buttons``.
A ``Button`` takes in a ``url`` fragment and the ``desc`` of the button
(the name that should be displayed for that button when rendered as html).

Both ``Button`` and ``ButtonGroup`` also take in keyword arguments as listed
:ref:`below <button_options>`

.. _button_options:

Button Options
--------------

``Button`` and ``ButtonGroup`` have the following options.

    ``kls``
        Css class to give to the html representation of the button.

        Defaults to None.

    ``display``
        A boolean used to make a button not show

    ``for_all``
        True if you want the button to appear in the changelist.

        False if you want the button to appear in the changeform.

        Defaults to False.

    ``condition``
        A boolean or callable (accepting the instance of the button and instance
        of the model being edited).

        This is used to say whether there is some condition against the button
        being shown.

    ``new_window``
        Whether clicking the button opens the new request in a new window.

        Defaults to False.

    ``needs_auth``
        If a boolean, says whether ``request.user.is_authenticated()`` needs to
        be True or not.

        If a string, or a list of strings, then the user must have all the
        permissions as specified by each string.

    ``description``
        A long description for the button. Currently only used for buttons
        in a ``ButtonGroup``

    ``save_on_click``
        Whether to save the form before redirecting to the view for that button.

        .. note:: This is set to False if you have ``for_all`` set to True.

    ``need_super_user``
        Whether you need to be super user for this button to be visible

    ``return_to_form``
        Whether to redirect straight back to the form after the button executes
        it's view.

        This works for both buttons that appear on change list and those that
        appear on the change form.

.. note:: When buttons are given to the template context so that they can be
  rendered by the :ref:`template <admin_templates>`, they are first wrapped in
  a ``cwf.admin.buttons.ButtonWrap`` which is a container that holds the button
  , the request context, and the the object being edited.

  This container proxies to the button and also provides some functions that
  interpret the options on the button against the request for the convenience
  of the template.

.. _button_html:
.. _button_clicking:

Button Html
-----------

When rendering a button, you have ``button.html`` available, which will return
the html that can be used to represent the button.

If the button has the ``save_on_click`` option, then it is rendered as an
"<input>" box that will submit the form before going into it's own view
, thus effectively saving the modifications you've made to the form before
doing anything else.

Otherwise, the button is rendered as an "<a>".

If you use the :ref:`templates <admin_templates>` provided, then it will also
make sure that the buttons that save the form are put at the bottom of the page
near the default "save" buttons that the admin provides.

Whereas buttons that don't save the form will appear at the top next to where
the admin already provides a button to see the history for an object.

Due to the css that the admin provides, these buttons will also have distinct
looks that signify this difference.
