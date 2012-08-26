from cwf.sections.section import Section
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

    ########################
    ###   USAGE
    ########################
    
    def load_admin(self, active_only=False):
        """Load all the admin.py files in each part so that they can register with the admin"""
        for part in self.each_part(active_only):
            part.load("admin")
    
    def models(self, active_only=False):
        """
            Get the models from each part and into one dictionary
            Doesn't care about duplicate model names
        """
        result = {}
        for part in self.each_part(active_only):
            models = part.load("models")
            if hasattr(models, '__all__'):
                for name in models.__all__:
                    result[name] = getattr(models, name)
        return result

    def urls(self, active_only=False, include_defaults=False):
        """
            Get a an object that holds the sections from each part
            Along with urlpatterns from this site
            and optionally everything in django.conf.urls.defaults
        """
        site = self.site(self.package, active_only)
        urls = {'site' : site, 'urlpatterns' : site.patterns()}
        if include_defaults:
            self.add_url_defaults(urls)
        return urls

    ########################
    ###   UTILITY
    ########################

    @property
    def imported_parts(self):
        if not hasattr(self, '_imported_parts'):
            self._imported_parts = True
            self.import_parts()
        return self.parts
    
    def each_part(self, active_only=False):
        """
            An iter that determines whether to go through all sections
            or just those that are "active"
        """
        for part in self.imported_parts:
            if not active_only or part.active:
                yield part

    def import_parts(self):
        """Import all the parts"""
        for part in self.parts:
            part.do_import(self.package)
    
    def site(self, name, active_only=True):
        """
            Create and return a site object that holds each section.
            Options for the add function is kept as self.kwargs in each part
        """
        site = Section(name, promote_children=True)
        for part in self.each_part(active_only):
            urls = part.load("urls")
            if urls and hasattr(urls, 'section'):
                site.add(urls.section, **part.kwargs)
        return site

    def add_url_defaults(self, urls):
        """Add django.conf.urls.defaults things to a dictionary"""
        from django.conf.urls import defaults
        for d in dir(defaults):
            if not d.startswith("_"):
                urls[d] = getattr(defaults, d)

########################
###   PART
########################

class Part(object):
    """Object representing each part of a multi-part app"""
    def __init__(self, name, active=True, **kwargs):
        self.name = name
        self.active = active
        self.kwargs = kwargs
        
        # Add include_as if there is none already
        if type(name) in (str, unicode) and kwargs.get('include_as', None) is None:
            kwargs['include_as'] = self.name
    
    def do_import(self, package):
        """Get the package we are representing"""
        if type(self.name) not in (str, unicode):
            self.pkg = self.name
        
        elif type(package) not in (str, unicode):
            self.pkg = getattr(package, self.name)
        
        else:
            # We want an error from this to propagate
            pkg = __import__(package, globals(), locals(), [self.name], -1)
            self.pkg = getattr(pkg, self.name)
    
    def load(self, name):
        """Get a module from this package"""
        if not hasattr(self.pkg, name):
            # If it doesn't know about it, perhaps we need to import it
            try:
                __import__(self.pkg.__name__, globals(), locals(), [name], -1)
            except ImportError:
                # We don't care if there isn't anything to import
                pass
        
        if hasattr(self.pkg, name):
            return getattr(self.pkg, name)
