import types
import sys
import imp
import os

########################
###
###   EXECFILE
###
########################

def steal(*paths, **kwargs):
    glbs    = kwargs.get('globals', None)
    lcls    = kwargs.get('locals', None)
    folder  = kwargs.get('folder', None)
    prefix  = kwargs.get('prefix', None)
    environ = kwargs.get('environ', None)
    
    if not folder and environ:
        folder = os.environ[environ]
    
    if not folder or not glbs or not lcls:
        raise Exception, "Please supply a folder location, or environ variable, the globals dict and the locals dict"
    
    for p in paths:
        f = os.sep.join([folder, prefix.replace(".", os.sep), '%s.py' % p])
        execfile(f, glbs, lcls)

########################
###
###   CUSTOM IMPORTER
###
######################## 

class FileFaker(object):
    def __init__(self, names, values):
        self.names = names
        self.values = values
        
    def find_module(self, fullname, path=None):
        if fullname in self.names:
            return self
 
    def load_module(self, fullname):
        # Get the leaf module name and the directory it should be found in
        if '.' in fullname:
            package, leaf = fullname.rsplit('.', 1)
            path = sys.modules[package].__path__[0]
            if not path.endswith(os.sep):
                path = "%s%s" % (path, os.sep)
        else:
            leaf = fullname
            path = ''
 
        # Get the existing module or create a new one (for reload to work)
        module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        module.__file__ = '%s%s.py' % (path, leaf)
        module.__loader__ = self
        
        if callable(self.values):
            self.values = self.values()
        
        self.values = normalize_dict(self.values)
        
        # Populate the module namespace with the injected attributes
        module.__dict__.update(self.values)
            
        return module

def normalize_dict(d):
    """If the argument is a module, return the module's dictionary filtered
    by the module's __all__ attribute, otherwise return the argument as-is.
    If the module doesn't have an __all__ attribute, use all the attributes
    that don't begin with a double underscore."""
    if isinstance(d, types.ModuleType):
        keys = getattr(
            d,
            '__all__',
            filter(lambda k: not k.startswith('__'), d.__dict__.keys())
        )
        d = dict([(key, d.__dict__[key]) for key in keys])
    return d
    
def inject(obj, name, extra=None, prefix=None):
    if extra:
        for k, v in extra.items():
            setattr(obj, k, v)
    
    names = [name]
    if prefix:
        names.append("%s.%s" % (prefix, name))
          
    sys.meta_path.append(FileFaker(names, obj))
    
    
