.. _views_menu:

Menu Rendering
==============

.. currentmodule:: cwf.views.menu

.. autoclass:: Menu(request, section)

    If you use a :py:class:`cwf.views.base.View` then you will have one of these
    in ``request.state``
    (via the :py:meth:`get_state <cwf.views.base.View.get_state>` method)

    This is best used with the CWF :ref:`menu_templates`.

    .. automethod:: Menu.global_nav

    .. automethod:: Menu.side_nav
