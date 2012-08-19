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
            Called by dispatch
            determines what to call, calls it, creates template and renders it.
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
            If result is None, then raise 404

            Get either (template, extra) tuple from result and render that
                If template is None, then just return extra

            Or if result isn't a two item tuple, just return it as is
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
            Given a request and cleaned args and kwargs
            Look at the class to determine where target is
            And use it to get a result

            Raise Exception if can't find target
            raise 404 if we find a target but it returns nothing
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
        """Execute target with the request, args and kwargs"""
        return self.get_target(target)(request, *args, **kwargs)

    def has_target(self, target):
        """Says whether view has specified target"""
        return hasattr(self, target)

    def get_target(self, target):
        """Gets specified target from the view"""
        return getattr(self, target)

    def clean_view_kwargs(self, kwargs):
        """Clean kwargs that are to be sent to the target view"""
        for key, item in kwargs.items():
            kwargs[key] = self.clean_view_kwarg(key, item)
        return kwargs

    def clean_view_kwarg(self, key, item):
        """
            Clean a single view kwarg
            If it's a string, make sure it has no trailing slashes
            Otherwise just return
        """
        if type(item) in (str, unicode):
            while item.endswith("/"):
                item = item[:-1]
        return item
    
    ########################
    ###   STATE
    ########################

    def get_state(self, request, target):
        """Get a state object for this request"""
        path = self.path_from_request(request)
        base_url = self.base_url_from_request(request)
        if base_url != '' and path[0] == '':
            path.pop(0)

        menu = Menu(request, path)
        return DictObj(
              menu = menu
            , path = path
            , target = target
            , base_url = base_url
            )

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
            path.insert(1, '')

        return path
