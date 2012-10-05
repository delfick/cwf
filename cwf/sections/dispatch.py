'''
    Central dispatch logic for all dispatched views
'''
class Dispatcher(object):
    '''
        Object used to determine what function to call for a request
        Will find correct class and then use target view as the function to call
        Will also cache views
    '''
    def __init__(self):
        self.views = {}

    @property
    def __name__(self):
        """
            Non-threadsafe hack to make amonpy happy
            And to make the dispatcher object wrappable by the wraps decorator
        """
        if hasattr(self, 'view') and hasattr(self, 'target'):
            return "Dispatcher: %s:%s" % (self.view.__class__.__name__, self.target)
        else:
            return self.__class__.__name__

    def get_view(self, location):
        '''Ensure view for given location is in self.views and then return that view'''
        if location not in self.views:
            self.views[location] = self.find_view(location)
        return self.views[location]

    def find_view(self, location):
        '''Find the kls for the given location and return an instance of this kls'''
        if type(location) not in (unicode, str):
            # Already a class
            return location
        else:
            obj = location.split('.')
            path, name = obj[:-1], obj[-1]
            pkg = __import__('.'.join(path), globals(), locals(), [name], -1)
            return getattr(pkg, name)()

    def __call__(self, request, kls, target, *args, **kwargs):
        '''
            For this kls and target return the result of invoking the correct view
            It is assumed this is created by Section.patterns in which case Http404 is already raised if section is unreachable
        '''
        view = self.get_view(kls)
        self.view = view
        self.target = target
        return view(request, target, *args, **kwargs)

dispatcher = Dispatcher()
