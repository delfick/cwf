"""
    Subclasses of :py:class:`cwf.views.base.View` that override the :py:meth:`cwf.views.base.View.execute` method.

    The ``execute`` method is used to get a view for the ``target`` to render and call it.

    These classes overwrite this behaviour to restrict or modify the result of calling the target.
"""
from django.contrib.admin.views.decorators import staff_member_required
from base import View

class StaffView(View):
    """Restrict to staff members"""
    def execute(self, target, request, args, kwargs):
        """
            Use the django provided
            `staff_member_required <https://github.com/django/django/blob/master/django/contrib/admin/views/decorators.py>`_
            decorator to ensure only staff members can access any target on this class.
        """
        def view(request, *args, **kwargs):
            return super(StaffView, self).execute(target, request, args, kwargs)
        return staff_member_required(view)(request, *args, **kwargs)

class LocalOnlyView(View):
    """Restrict to local users only"""
    def execute(self, target, request, args, kwargs):
        """
            Raise a 404 if the Remote Address of the user is not 127.0.0.1.

            Otherwise proceed as normal.
        """
        ip = request.META.get('REMOTE_ADDR')
        if ip != '127.0.0.1':
            self.renderer.raise404()
        return super(LocalOnlyView, self).execute(target, request, args, kwargs)

class JSView(View):
    """Convert target output into a json response"""
    def execute(self, target, request, args, kwargs):
        """
            Assume the result of calling the target returns ``(template, data)``.

            Proceed to return the data as a :py:meth:`json response <cwf.views.rendering.Renderer.json>`
        """
        result = super(JSView, self).execute(target, request, args, kwargs)
        template, data = result
        return self.renderer.json(data)
