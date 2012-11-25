.. _sections_menus:

Generated Menus
===============

One of the points of CWF is that it provides an API you can use to generate
your urlpatterns and menu system from without repeating yourself.

So part of the :ref:`options <section_configure>` available is about saying
how the sections are represented in the menu system.

.. _section_configure_menu:

Section menu options
--------------------

The options available that directly affect how a section appears in the
menu are as follows:

    ``admin``
        Hardcode that a section should be displayed as only available via
        admin privelege.

    ``display``
        Whether to show this section at all.

        Note that this option will not propogate to it's children if the
        ``propogate_display`` option is False.

    ``alias``
        What name is displayed to the end user for this section.

    ``values``
        Allows you to have this section appear multiple times
        with different values. See :ref:`section_values`

    ``promote_children``
        Whether to display the children of this section at the same level
        as this section. See :ref:`promoted_sections`

    ``propogate_display``
        Whether the ``display`` option should be propogated to a section's
        children.

.. _section_values:

Section Values
++++++++++++++

.. _promoted_sections:

Promoted Sections
+++++++++++++++++
