.. _menu_templates:

Menu Templates
==============

There is only one template supplied for rendering the menus, which is found
inside the "templates/menu" folder under cwf root. It's name is ``base.html``
and it can be used to recursively generate the menu system.

.. note:: As long as it is :ref:`available <template_availability>` and it has the
  :ref:`menu object <section_menu_obj>`.

It uses the following variables:

    ``children_template``
        What template it should use to render the children. This can be set to
        the same template you are starting the generation from.

        i.e. ::

            {% include "menu/base.html" with menu=menu.global_nav children_template="menu/base.html" ignore_children='True' %}

    ``menu``
        The menu object we're getting the sections from.

    ``ignore_children``
        Boolean that says if we should ignore displaying children at all
        regardless of whether a section actually has children.

        This is useful for displaying a global navigation where you only want
        the root level navs with none of their children.

And supplies the following blocks that you can override:

    ``selected_item_attrs``
        The attributes given to ``<li>`` sections that represent
        a selected section.

    ``unselected_item_attrs``
        The attributes given to ``<li>`` sections that do not represent
        a selected section

    ``item_link``
        Determine what to display as the link inside each ``<li>``.

    ``item_children``
        Determine what to display as children for a section.

It will make sure that each list of children is wrapped in an ``<ul>`` and that
sections that don't have children will not output an empty ``<ul></ul>``.
