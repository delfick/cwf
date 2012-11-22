.. _templatetags_index:

Template Tags
=============

CWF contains two custom templatetags that it uses when it's constructing the
template for the :ref:`menu generation <cwf_menus>` functionality provided.

These are:

    :ref:`tag-varset`
        Used to create a variable in the template from a block

    :ref:`tag-wrapped`
        Used to create a html element only if the body of the block provided
        isn't empty

.. _tag-varset:

varset
------

Usage for this tag is::

    {% load varset %}
    {% varset name_of_new_variable %}
        {% if some_condition %}
            {{some_value}} blah
        {% else %}
            another value
        {% endif %}
    {% endvarset %}

After we ``load`` the varset templatetags, we have available to us a tag called
``varset``. It takes the name of the variable to create
and will put the contents between the start of that tag till ``endvarset`` and
make that the value of the new variable, which can be used in your template any
point after this.

So in the example above, your template will now have a variable available called
``name_of_new_variable`` with whatever that block of code evaluates into.

.. _tag-wrapped:

wrapped
-------

Usage for this tag is::

    {% load wrapped %}
    {% wrapped li 'class="awesome" style="background-color:red"' %}
        {% if condition %}
            <p>wicked awesome</p>
        {% endif %}
    {% endwrapped %}

This allows us to create an html element that will only appear if it has
something inside of it.

So in the example above it will create::

    <li class="awesome" style="background-color:red">
        <p>wicked awesome</p>
    </li>

If ``condition`` is truthy. Otherwise, there isn't anything between the
``wrapped`` and ``endwrapped`` tags except for whitespace and so it won't even
output the ``<li>``.
