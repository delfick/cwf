from django.http import Http404

class Dispatcher(object):
    def __init__(self):
        self.viewObjs = {}
    
    def __getitem__(self, key):
        try:
            view = self.viewObjs[key]
        except KeyError:
            if type(key) in (unicode, str):
                obj = key.split('.')
                pkg = __import__('.'.join(obj[:-1]), globals(), locals(), [obj[-1]], -1)
                view = getattr(pkg, obj[-1])
            else:
                view = key
                key = key.__module__
            self.viewObjs[key] = view = view()
        
        return view
        
    def __call__(self, request, obj, target, section, condition, *args, **kwargs):
        if callable(condition):
            condition = condition()
        
        needsAuth = False
        if section.options.needsAuth and not request.user.is_authenticated:
            needsAuth = True
        
        if not condition and not needsAuth:
            view = self[obj]
            state = view.getState(request)
            return self[obj](state, target, section=section, *args, **kwargs)
        
        raise Http404
    
dispatch = Dispatcher()
