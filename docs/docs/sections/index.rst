.. toctree::
    :hidden:

    sections
    urls
    views
    menus

.. _sections_index:

Sections
========

CWF was built for and based on the idea that your website can be split into
several sections that have their own urls and views; and that the menus for
each section map directly to your urls.

Provided under the ``cwf.sections`` namespace is functionality that can be used
to define these sections.

The idea is then you either include the urlpatterns created just as if you
defined them by hand, or use the :ref:`cwf.splitter <splitter_index>` logic
to combine the sections into your website.

The following pages guide you through what is possible here:

    :doc:`sections`
        An introduction to what a Section is.

    :doc:`urls`
        The options available to alter the url for a section.

    :doc:`views`
        How to say what views should be invoked by a url.

    :doc:`menus`
        How to alter the look of the menu that is generated.
