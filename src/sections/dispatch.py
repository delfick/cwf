'''
    Central dispatch logic for all views
'''
from django.http import Http404

class Dispatcher(object):
    '''
        Object used to determine what function to call for a request
        Will find correct class and then use target view as the function to call
        Will make sure request has permission for the view first
        Will also cache views
    '''
    def __init__(self):
        self.views = {}
        
    def get_view(self, location):
        '''Ensure view for given location is in self.views and then return that view'''
        if view not in self.views:
            self.views[view] = self.find_view(view)
        return self.views[view]
    
    def find_view(self, location):
        '''Find the kls for the given location'''
        if type(location) not in (unicode, str):
            # Already a class
            return location
        else:
            obj = key.split('.')
            path, name = key[:-1], key[-1]
            pkg = __import__('.'.join(path), globals(), locals(), [name], -1)
            return getattr(pkg, name)
    
    def __call__(self, request, kls, target, *args, **kwargs):
        '''
            For this location, target, section and condition return the result of invoking the correct view
            If no appropiate view found or request doesn't have permissions, a 404 will be raised
        '''
        # Non-threadsafe hack to make amonpy happy
        self.__name__ = self.__class__.__name__
        section = kwargs['section']
        if section and section.reachable(request):
            view = self.get_view(kls)
            self.__name__ = "Dispatcher: %s:%s" % (view.__class__.__name__, target)
            return view(request, target, *args, **kwargs)
        
        raise Http404

dispatcher = Dispatcher()
