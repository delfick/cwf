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

There exists a situation where a section can contain multiple values and you
want your menu to display all those possible values.

CWF provides the ``values`` option for specifying this.

This option should be set to an object with a ``get_info`` method that returns
a list of [(url, alias), (url, alias), ...] where each pair represents another
value.

To assist with this, CWF provides the ``cwf.sections.Values`` object.

.. note:: This functionality will also work with child sections such that each
  value will get all the children of the original section and those children may
  have their own collection of values and so on.

The ``Values`` object takes the following options:
    
    ``values``
        The values to use.

        This can be a list of [value, value, value, ...].

        Or it can be a callable 
        lambda ((request, parent_url_parts, path)) : [value, value, value, ...]

        Where request is the ``request`` object, ``path`` is a list of the parts
        that makes up the current url. And ``parent_url_parts`` is all the parts
        in the url leading up to the parent of the current section.

    ``each``
        A callable
        lambda ((request, parent_url_parts, path), value) : (url, alias)

        If this isn't set, then the ``alias`` and ``url`` will both be set
        to the ``value`` provided by the ``values`` option.

    ``sorter``
        If it's Falsey then no sorting will occur.

        If it's Truthy then the values are sorted.

        If it's a callable, then the values are sorted and ``sorter`` is used
        as the second argument to the python ``sorted`` function.

    ``as_set``
        Say whether to remove duplicate values before we work out the ``alias``
        and ``url`` for each value.

    ``sort_after_transform``
        Whether to sort after or before we determine the ``alias`` and ``url``
        for each value.

For example:

.. code-block:: python
    
    section = Section().configure(''
        , target = 'nlsBase'
        , alias  = 'NewsLetters'
        )

    ye = section.add('\d{4}').configure(''
        , target = 'newsYear'
        , match  = 'year'
        , values = V(
            lambda _ : [date.year for date in News.objects.dates("pubDate", "year", "DESC")]
          , as_set = False
          )
        )

    item = ye.add('\d+', name="newsitem").configure(''
        , target = 'newsItem'
        , match  = 'item'
        , values = V(
            lambda (r, parent, p) : News.objects.filter(pubDate__year=parent[-1]).order_by('-pubDate')
          , lambda _, value : (value.pk, unicode(value))
          , as_set  = False
          )
        )

    item.add("example1").configure(target="example")
    item.add("example2").configure(target="example")

This here will be used by the menu generation to produce a menu structure that
looks like::

    2012
        News Item 1
            example1
            example2
        News Item 2
            example1
            example2

    2011
        News Item 3
            example1
            example2
        News Item 4
            example1
            example2
        News Item 5
            example1
            example2

Depending on the values in the database table being used here.

.. note:: CWF doesn't implement any kind of caching yet, so these functions will
  be called every time the menu is generated.

.. _promoted_sections:

Promoted Sections
+++++++++++++++++

CWF provides the ``promote_children`` :ref:`configuration <section_configure>`
option for saying that the child of a section should appear in the menu at
the same level as that section.

So for example, say we want to have common settings grouped but keep everything
at one level:

.. code-block:: python

    section = Section().configure(''
        , target = 'base'
        )

    group1 = section.add("group1").configure(
        , module="webthing.groupone"
        , promote_children=True
        )
    group1.add("one").configure(target="one")
    group1.add("two").configure(target="two")

    group2 = section.add("group1").configure(''
        , module="webthing.grouptwo"
        , promote_children=True
        )
    group2.add("three").configure(target="three")
    group2.add("four").configure(target="four")

Then we'll get a menu that looks like::

    one
    two
    three
    four

Instead of::

    group1
        one
        two
    group2
        three
        four

.. note:: Currently there is a limitation that sections that promote their
  children are unable to contribute to the url and therefore, children of these
  sections cannot use the values used by the parent section.

Creating the menu
-----------------

You use the ``cwf.views.menu:Menu`` class to generate the menu system from a
section for a particular request.

.. code-block:: python

    from cwf.views.menu import Menu

    def my_view_function(request):
        menu = Menu(request, request.section)

        # Add menu to your template context
        # And do everything else as normal

.. note:: If you add your views using Section, then the view you provide will be
  wrapped in a function that attaches that ``section`` to the ``request`` object
  before calling your original view

Then in your template::

    # For the global navigation
    {% include "cwf/menu/base.html" with menu=menu.global_nav children_template="menu/base.html" ignore_children='True' %}

    # For the side navigation
    {% include "cwf/menu/base.html" with menu=menu.side_nav children_template="menu/base.html" %}

To understand how to make these templates available and how to customise them
, you should read the section on :ref:`templates_index`.
