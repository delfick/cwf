from .urls.section import Site
        
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
            module = part.get("models", '__all__', [])
            for model in models:
                locals()[model.__name__] = model
    
    def admin(self, theLocals, activeOnly=False):
        """Load all the admin.py files in each part so that they can register with the admin"""
        for part in self._iter(activeOnly):
            part.get("admin")
    
    def site(self, name, activeOnly=False):
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
            if activeOnly or not part.active:
                yield part
        
########################
###
###   PART
###
########################

class Part(object):
    """Object representing each part of a multi-part app"""
    def __init__(self, name, active, **kwargs):
        self.name = name
        self.active = active
        self.kwargs = kwargs
        self.pkg = None
    
    def _import(self, package, theGlobals, theLocals):
        """Get the package we are representing"""
        if type(self.name) not in (str, unicode):
            self.pkg = self.name
        
        elif type(package) not in (str, unicode):
            self.pkg = getattr(package, self.name)
        
        else:
            self.pkg = __import__('%s.%s' % (package, self.name), theGlobals, theLocals, [], -1)
        
    def get(self, name, attr=None, default=None):
        """Get a module from this package
        Then optionally a particular attribute from that module
        Or if there is no such attr, a default value
        """
        ret = default
        if hasattr(self.pkg, name):
            ret = getattr(self.pkg, name)
            if attr:
                ret = getattr(ret, attr)
    
        return ret
        
        
        
