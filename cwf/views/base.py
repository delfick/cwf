from rendering import renderer
from menu import Menu

import json
import re

regexes = {
    'multi_slash' : re.compile('/+')
    }

class DictObj(dict):
    """Dictionary with attribute access"""
    def __init__(self, *args, **kwargs):
        super(DictObj, self).__init__(self, *args, **kwargs)
        self.__dict__ = self

class View(object):
    """Base class for cwf views"""
    def __init__(self):
        self.renderer = renderer

    def __call__(self, request, target, *args, **kwargs):
        """
            When an instance of the view class is called, it will do the following:

                * Create :ref:`view state <views_view_state>`
                * :ref:`Clean kwargs <views_view_kwargs>`
                * Get a :ref:`result <views_view_result>` to render
                * :ref:`Render <views_view_rendering>` the result and return.
        """
        # Get state to put onto the request
        request.state = self.get_state(request, target)

        # Clean the kwargs
        cleaned_kwargs = self.clean_view_kwargs(kwargs)

        # Get the result to render
        result = self.get_result(request, target, args, cleaned_kwargs)

        # Render the result
        return self.rendered_from_result(request, result)

    def rendered_from_result(self, request, result):
        """
            If the result being rendered is ``None``, then a ``Http404`` will be raised.

            If the result is a list or tuple of two items, then it assumes this list
            represents ``(template, extra)`` where ``template`` is the name of the template
            to render and ``extra`` is any extra context to render the template with.

            If ``template`` is None, then ``extra`` is returned, otherwise it uses the
            :py:meth:`cwf.views.rendering.Renderer.render` to render the template and context.

            If the result to render is not a two item tuple or list, then it just returns
            it as is.
        """
        # No result to render, raise 404
        if result is None:
            self.renderer.raise404()

        if type(result) in (tuple, list) and len(result) == 2:
            template, extra = result
        else:
            return result

        # Return extra as is if template is None
        if template is None:
            return extra

        # Return the response
        return self.renderer.render(request, template, extra)

    ########################
    ###   GETTING A RESULT
    ########################

    def get_result(self, request, target, args, kwargs):
        """
            Takes the ``request`` object, the ``target`` that is been called
            and any positional arguments and :ref:`cleaned <views_view_kwargs>` keyword arguments
            and returns a result that will be :ref:`rendered <views_view_rendering>`.

            If the instance has an ``override`` method
            , then it will pass all those arguments in that function and return it's result.

            Otherwise:

            Use :py:meth:`View.has_target` to check if the ``target`` exists on the instance
            and raise an exception if it does not exist.

            If the ``target`` does exist, then pass it into :py:meth:`View.execute`
            along with the ``request``, ``args`` and cleaned ``kwargs`` to get a result.

            If the result is a callable then call it with the ``request`` and return what that gives back.

            Otherwise, return the result as is.
        """
        # If class has override method, use that instead
        if hasattr(self, 'override'):
            return self.override(request, target, args, kwargs)

        # Complain if there is no target
        if not self.has_target(target):
            raise Exception, "View object doesn't have a target : %s" % target

        # We have the target, get result from it
        result = self.execute(target, request, args, kwargs)

        # If the result is callable, call it with request and return
        if callable(result):
            return result(request)
        else:
            return result

    def execute(self, target, request, args, kwargs):
        """
            Execute target with the request, args and kwargs.

            By default this means getting a callable for the ``target`` using :py:meth:`View.get_target`
            and calling it with the ``request``, ``*args`` and ``**kwargs``.
        """
        return self.get_target(target)(request, *args, **kwargs)

    def has_target(self, target):
        """
            Return whether view has specified target

            By default, just use hasattr on the instance
        """
        return hasattr(self, target)

    def get_target(self, target):
        """
            Return callable for the ``target`` from this instance.

            By default, just use getattr on the instance.
        """
        return getattr(self, target)

    def clean_view_kwargs(self, kwargs):
        """Replace all kwargs with the result of passing them through ``clean_view_kwarg``"""
        for key, item in kwargs.items():
            kwargs[key] = self.clean_view_kwarg(key, item)
        return kwargs

    def clean_view_kwarg(self, key, item):
        """
            Clean a single view kwarg

            If it's a string, make sure it has no trailing slashes
            , otherwise just return it as is.
        """
        if type(item) in (str, unicode):
            while item.endswith("/"):
                item = item[:-1]
        return item

    ########################
    ###   STATE
    ########################

    def get_state(self, request, target):
        """
            Return an object that can be used to store state for a request.

            For convenience, this object behaves like a Javascript object (supports both
            dot notation and array notation for accessing and setting variables).

            When it's created, it is initialized with some values:

                ``menu``
                    If we got here via a CWF Section, then we will be able to create
                    a :py:class:`cwf.views.menu.Menu` object from that section.

                ``path``
                    The path of the request with no leading, trailing; or duplicate slashes.

                ``target``
                    The target being reached on the class.

                ``section``
                    The CWF section that is executing this view (if one was used)

                ``base_url``
                    ``request.META.get('SCRIPT_NAME', '')``
        """
        path = self.path_from_request(request)
        section = self.get_section(request, path)
        base_url = self.base_url_from_request(request)
        if base_url != '' and path[0] == '':
            path.pop(0)

        menu = None
        if section:
            menu = Menu(request, section)

        return DictObj(
              menu = menu
            , path = path
            , target = target
            , section = section
            , base_url = base_url
            )

    def get_section(self, request, path):
        """Get a section from the request object"""
        return getattr(request, 'section', None)

    ########################
    ###   UTILITY
    ########################

    def base_url_from_request(self, request):
        """Get base url for this request"""
        return request.META.get('SCRIPT_NAME', '')

    def path_from_request(self, request):
        """Determine the path for this request"""
        path = request.path
        if path:
            path = regexes['multi_slash'].sub('/', request.path)

        path = [p.lower() for p in path.split('/')]

        if path and path[-1] != '':
            path.append('')

        if path and path[0] != '':
            path.insert(0, '')

        return path
