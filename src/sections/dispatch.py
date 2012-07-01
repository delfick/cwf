'''
    Central dispatch logic for all views
'''
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
        if location not in self.views:
            self.views[location] = self.find_view(location)
        return self.views[location]
    
    def find_view(self, location):
        '''Find the kls for the given location'''
        if type(location) not in (unicode, str):
            # Already a class
            return location
        else:
            obj = location.split('.')
            path, name = obj[:-1], obj[-1]
            pkg = __import__('.'.join(path), globals(), locals(), [name], -1)
            return getattr(pkg, name)
    
    def __call__(self, request, kls, target, *args, **kwargs):
        '''
            For this location, target, section and condition return the result of invoking the correct view
            It is assumed this is created by Section.patterns in which case Http404 is already raised if section is unreachable
        '''
        # Non-threadsafe hack to make amonpy happy
        self.__name__ = self.__class__.__name__
        view = self.get_view(kls)
        self.__name__ = "Dispatcher: %s:%s" % (view.__class__.__name__, target)
        return view(request, target, *args, **kwargs)

dispatcher = Dispatcher()
