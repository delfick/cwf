from cwf.urls.section import Site
from inject import inject

import __builtin__
import inspect
import sys
        
########################
###
###   PARTS
###
########################

class Parts(object):
    """Object that holds Part objects and has methods for getting models, admin or site from them"""
    def __init__(self, package, *parts):
        self.package = package
        self.parts = parts
        for part in self.parts:
            part._import(package)
    
    def models(self, activeOnly=False):
        """Put all the models from each part in the local space of the models.py this is called from"""
        mdls = {}
        for part in self._iter(activeOnly):
            models = part.get("models", '__all__', [])
            for model in models:
                mdls[model.__name__] = model
        
        return mdls

    def urls(self, activeOnly=False, includeDefaults=False):
        site = self.site(self.package)
        urls = {'site' : site, 'urlpatterns' : site.patterns()}
        if includeDefaults:
            from django.conf.urls import defaults
            for d in dir(defaults):
                if not d.startswith("_"):
                    urls[d] = getattr(defaults, d)
        return urls
    
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
        
########################
###
###   Configure
###
########################
        
def configure(settings, package, *parts, **kwargs):
    if not hasattr(settings, 'PARTCONFIG'):
        settings.PARTCONFIG = {}
    
    config = Parts(package, *parts)
    settings.PARTCONFIG[package] = config
    
    # get the models
    models = config.models()
    
    # get the urls
    includeDefaults = kwargs.get("includeDefaultUrls", False)
    urls = lambda : config.urls(includeDefaults=includeDefaults)
    
    # Inject everything
    prefix=kwargs.get("prefix", None)
    inject(models, '%s.models' % package, prefix=prefix)
    inject(urls,   '%s.urls'   % package, prefix=prefix)
    
    # Load in the admin configuration for this package
    config.admin()
        
########################
###
###   FAILED IMPORTS
###
########################
        
def installFailedImportHandler():
    """
        Custom __import__ function that records failed imports
        Useful if say you're using werzeug auto reloader
        This way, failed imports are still checked for changes
    """
    original_import = __builtin__.__import__
    def new_import(name, *args, **kwargs):
        # Naively cope with the situation where this is called as a method
        if type(name) not in (str, unicode) and len(args) > 0:
            args = list(args)
            name = args.pop(0)
        
        failed = None
        try:
            return original_import(name, *args, **kwargs)
        
        except SyntaxError, s:
            # Record failed import and propogate error
            failed = (name, s.filename)
            raise
        
        except Exception, i:
            if not isinstance(i, ImportError):
                # ImportError is probably a legitimate fail
                failed = (name, inspect.trace()[-1][1])
            raise
        
        finally:
            if failed:
                # Import failed, put in fake module so that werkzeug knows to see if it's been changed
                name, filename = failed
                sys.modules[name] = type('FailedImport', (object, ), {'__file__' : filename})
    
    __builtin__.__import__ = new_import