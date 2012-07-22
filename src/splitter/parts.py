from src.sections.section import Section
from imports import inject

########################
###   PARTS
########################

class Parts(object):
    """
        Object that holds Part objects
        Has methods for getting models, admin or site from the parts
    """
    def __init__(self, package, *parts):
        self.parts = parts
        self.package = package

        # Import our parts
        for part in self.parts:
            part._import(package)
    
    def models(self, active_only=False):
        """
            Get the models from each part and into one dictionary
            Doesn't care about duplicate model names
        """
        models = {}
        for part in self._iter(active_only):
            for model in part.retrieve("models", attr='__all__', default=[])
                models[model.__name__] = model
        return models

    def urls(self, active_only=False, include_defaults=False):
        """
            Get a an object that holds the sections from each part
            Along with urlpatterns from this site
            and optionally everything in django.conf.urls.defaults
        """
        site = self.site(self.package)
        urls = {'site' : site, 'urlpatterns' : site.patterns()}
        if include_defaults:
            from django.conf.urls import defaults
            for d in dir(defaults):
                if not d.startswith("_"):
                    urls[d] = getattr(defaults, d)
        return urls
    
    def load_admin(self, active_only=False):
        """Load all the admin.py files in each part so that they can register with the admin"""
        for part in self._iter(active_only):
            part.retrieve("admin")
    
    def site(self, name, active_only=True):
        """
            Create and return a site object that holds each section.
            Options for the add function is kept as self.kwargs in each part
        """
        site = Section(name, promote_children=True)
        for part in self._iter(active_only):
            section = part.retrieve('urls', attr='section', default=None)
            if section:
                site.add(section, **part.kwargs)
        return site
    
    def __iter__(self):
        """Iterate through all sections"""
        for part in self.parts:
            yield part
    
    def _iter(self, active_only=False):
        """
            An iter that determines whether to go through all sections
            or just those that are "active"
        """
        for part in self:
            if not active_only or part.active:
                yield part

########################
###   PART
########################

class Part(object):
    """Object representing each part of a multi-part app"""
    def __init__(self, name, active=True, **kwargs):
        self.pkg = None
        self.name = name
        self.active = active
        self.kwargs = kwargs
        
        if kwargs.get('include_as', None) is None:
            kwargs['include_as'] = self.name
    
    def _import(self, package):
        """Get the package we are representing"""
        if type(self.name) not in (str, unicode):
            self.pkg = self.name
        
        elif type(package) not in (str, unicode):
            self.pkg = getattr(package, self.name)
        
        else:
            # We want an error from this to propagate
            pkg = __import__(package, globals(), locals(), [self.name], -1)
            self.pkg = getattr(pkg, self.name)
        
    def retrieve(self, name, attr=None, default=None):
        """
            Get a module from this package
            Then optionally a particular attribute from that module
            Or if there is no such attr, a default value
        """
        ret = default
        if not hasattr(self.pkg, name):
            # If it doesn't know about it, perhaps we need to import it
            try:
                __import__(self.pkg.__name__, globals(), locals(), [name], -1)
            except ImportError:
                # We don't care if there isn't anything to import
                pass
        
        if hasattr(self.pkg, name):
            ret = getattr(self.pkg, name)
            if attr:
                ret = getattr(ret, attr)
        
        return ret
