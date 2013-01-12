.. _views_special:

Special Views
=============

CWF provides three subclasses of the :ref:`Base View <views_base>` as a
convenience.

All three of them inherit from the Base View and only override the ``execute``
method, which is the one used to get a view for the ``target`` to render and
call it.

Staff View
----------

Makes sure that the current user is a staff member before executing the target.

It uses the ``staff_member_required``
`decorator <https://github.com/django/django/blob/master/django/contrib/admin/views/decorators.py>`_
that Django provides.

Local Only View
---------------

Makes sure that the remote ip of the user is 127.0.0.1 before executing the
target.

It will raise a 404 if the remote ip is not 127.0.0.1.

JSView
------

Assumes that the result from a normal ``self.execute`` is ``(template, data)``;
proceeds to ignore the ``template`` and returns the ``data`` as
:ref:`rendered json <views_rendering_json>`
