from cwf_new.urls.section import Site
        
########################
###
###   PARTS
###
########################

class Parts(object):
    """Object that holds Part objects and has methods for getting models, admin or site from them"""
    def __init__(self, package, theGlobals, theLocals, *parts):
        self.parts = parts
        for part in self.parts:
            part._import(package, theGlobals, theLocals)
    
    def models(self, theLocals, activeOnly=False):
        """Put all the models from each part in the local space of the models.py this is called from"""
        for part in self._iter(activeOnly):
            models = part.get("models", '__all__', [])
            for model in models:
                theLocals[model.__name__] = model
    
    def admin(self, activeOnly=False):
        """Load all the admin.py files in each part so that they can register with the admin"""
        for part in self._iter(activeOnly):
            part.get("admin")
    
    def site(self, name, activeOnly=True):
        """Create and return a site object that holds each section.
        Options for the add function is kept as self.kwargs in each part"""
        site = Site(name)
        for part in self._iter(activeOnly):
            section = part.get("urls", 'section', None)
            if section:
                site.add(section, **part.kwargs)
        
        return site
    
    def __iter__(self):
        """Iterate through all sections"""
        for part in self.parts:
            yield part
    
    def _iter(self, activeOnly=False):
        """An iter that determines whether to go through all sections or just those that are "active" """
        for part in self:
            if not activeOnly or part.active:
                yield part
        
########################
###
###   PART
###
########################

class Part(object):
    """Object representing each part of a multi-part app"""
    def __init__(self, name, active=True, **kwargs):
        self.pkg = None
        self.name = name
        self.active = active
        self.kwargs = kwargs
        
        if kwargs.get('includeAs', None) is None:
            kwargs['includeAs'] = self.name
    
    def _import(self, package, theGlobals, theLocals):
        """Get the package we are representing"""
        if type(self.name) not in (str, unicode):
            self.pkg = self.name
        
        elif type(package) not in (str, unicode):
            self.pkg = getattr(package, self.name)
        
        else:
            # We want an error from this to propagate
            pkg = __import__(package, theGlobals, theLocals, [self.name], -1)
            self.pkg = getattr(pkg, self.name)
        
    def get(self, name, attr=None, default=None):
        """Get a module from this package
        Then optionally a particular attribute from that module
        Or if there is no such attr, a default value
        """
        ret = default
        if not hasattr(self.pkg, name):
            # If it doesn't know about it, perhaps we need to import it
            try:
                __import__(self.pkg.__name__, globals(), locals(), [name], -1)
            except ImportError, error:
                pass
            
        if hasattr(self.pkg, name):
            ret = getattr(self.pkg, name)
            if attr:
                ret = getattr(ret, attr)
    
        return ret
        
        
        
