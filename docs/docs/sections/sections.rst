.. _sections_sections:

A CWF Section
=============

In Django, you define the urls in your site by creating urlpatterns.

This is usually done by hand, but this means that if you want to generate a
menu system on your site from your urls, you have to essentially duplicate the
structure of your website.

CWF instead provides classes that can be used to generate both the urlpatterns
and a data structure that can be used to generate a menu from.

Usage looks like:

.. code-block:: python

    from cwf.sections import Section

    section = Section().configure(module="webthing.views")

    section.first(name="root").configure(target='base')
    section.add('login', name='login').configure(target='login')
    section.add('logout', name='logout').configure(target='logout')

    numbers = section.add('numbers')
    numbers.add("one").configure(target="one")
    numbers.add("two").configure(target="two")

    section.add('\d+').configure(''
        , target='digits'
        , match='digit'
        )

    urlpatterns = section.patterns()

For this very simple case, it would be the same as:

.. code-block:: python

    from django.conf.urls import patterns

    urlpatterns = patterns(''
        , (r'^$', 'webthing.views.base', name="root")
        , (r'^login/$', 'webthing.views.login', name="login")
        , (r'^logout/$', 'webthing.views.logout', name="logout")
        , (r'^numbers/one/$', 'webthing.views.one')
        , (r'^numbers/two/$', 'webthing.views.two')
        , (r'^(?P<digit>\d+)/$', 'webthing.views.digits')
        )

.. _section_configure:

Configuring a section
---------------------

Every section has an ``options`` object that knows what options are available
, what values those options can be, and some helpful methods for determining
information about the section from those options.

You can configure these options by using "section.configure".

For example:

.. code-block:: python

    tests = section.add("tests").configure(''
        , kls = 'testViews'
        , redirect = 'register'
        , needs_auth = True
        )

.. note:: Positional arguments to configure are ignored.

There are options available for how the section appears in the
:ref:`urlpatterns <section_configure_url>`
; what :ref:`view <section_configure_url>` is used; and how it appears in the
:ref:`menu <section_configure_menu>` that can be generated.

.. _section_children:

Adding child sections
---------------------

Sections represent only one part of the url. To make urls with more than one
part to it, we need to build up a heirarchy of sections. We can do this by
adding child sections to each section.

When we then did "section.first" and "section.add" we created new sections with
the ``url`` and ``name`` as passed into those functions and these new sections
got the first section as it's ``parent``. The first section also records these
new sections on itself.

.. note:: section.first() behaves exactly as section.add() except the section
  will consider this child section to be first before any other child sections
  and there can only be one "first" section.

You can also add sections via the ``merge``, ``adopt`` and ``copy`` functions on
the section.

.. note:: Creating a section this way will copy most options from the parent
  onto the child.

Adding a Child
++++++++++++++

The "section.first" and "section.add" methods are shortcuts to
"section.add_child" where the only difference is "section.first" will call
"add_child" with "first=True"

"section.first" will also default url to an empty string, whereas "section.add"
will complain if no url is provided.

These functions will return the child that was added.

.. _section_merge:

Merging children
++++++++++++++++

If you do a "section.merge(another_section)", then you will add the children
from ``another_section`` onto ``section``.

If you specify ``take_base=True``, then it will also take the first child of
``another_section`` and put it onto ``section`` as the first child.

.. note:: merging always does a :ref:`copy <section_copy>`.

.. _section_adoption:

Adopting children
+++++++++++++++++

You may do a "section.adopt(other_section1, other_section2)" and it will change
the parent of these children to ``section``
and add them as children of ``section``.

If you also specify "clone=True", then it will use
:ref:`section.copy <section_copy>` to make a clone of the children before
adding them as children.

You may also specify as keyword arguments ``consider_for_menu``
and ``include_as`` and these will be used when putting the child onto the
``section``. See :ref:`section_datastructure` for what that means.

.. _section_copy:

Copying children
++++++++++++++++

Doing a "section.copy(other_section)" will make a :ref:`clone <section_clone>`
of ``other_section`` and recursively :ref:`merge <section_merge>` the children
of ``other_section`` onto the clone before adding the clone as a child of
``section``.

It will also take in ``consider_for_menu`` and ``include_as``
(see :ref:`section_datastructure`)

.. _section_clone:

Cloning children
++++++++++++++++

You can use the "section.clone()" method to create a clone of the ``section``.

It will create a new Section object with the ``url``, ``name`` and ``parent`` of
the ``section`` being cloned and then copy a clone of "section.options" onto the
clone.

It will not pass on any reference or clone of the children from the original
section onto the clone.

.. _section_datastructure:

Section datastructure
---------------------

The section has two attributes it uses to hold it's children:

    ``_base``
        This holds a single :ref:`item <section_item>`.
        And is what the section considers as the "first" child.

    ``_children``
        An array of :ref:`items <section_item>`.

.. _section_item:

Section Item
++++++++++++

There are three pieces of information that is required to make it easy for us
to generate a menu from this information: The section itself, whether to include
the section in the menu; and what to include the section as if it needs to be
included as anything special.

To achieve this, each child of a section is held in an instance of
``cwf.sections.section.Item``. This is an object that holds
``section``, ``consider_for_menu`` and ``include_as``.

This is so that sections can use the same sections as children but have them
appear in the menu and url scheme differently depending on which parent
owns them.
