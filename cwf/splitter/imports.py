import __builtin__
import inspect
import types
import sys
import imp
import os

########################
###   TAKING VARIABLES
########################

def steal(*filenames, **kwargs):
    """
        Steal variables from a bunch of files.
        filenames is the names of the files to steal from
        * Note that .py is appended to the end of them for you

        kwargs supplies:
          * globals : The globals dictionary to exec into
          * locals : The locals dictionary to exec into
          * folder : Folder where the files are
        It Will complain if neither folder, globals or locals are specified

        Variables are stolen using execfile
    """
    lcls = kwargs.get('locals', None)
    glbls = kwargs.get('globals', None)
    folder = kwargs.get('folder', None)

    # Complain about missing variables
    for name, val in [('folder', folder), ('globals', glbls), ('locals', lcls)]:
        if val is None:
            raise Exception("Please supply %s in kwargs" % name)

    # Exec the specified files into the globals and locals provided
    for filename in filenames:
        location = os.path.join(folder, "%s.py" % filename)
        execfile(location, glbls, lcls)

########################
###   INJECTING VARIABLES
########################

def inject(obj, *names):
    """
        Inject obj into import space
        Such that importing any of the names supplied gets back obj.

        If a name has dots in it like say 'a.b.c.d'
        Then from a.b.c import d will get back obj

        if a name has no dots in it like say 'e'
        Then import e will get back obj

        Will complain if no names are specified
    """
    # Be nice to being able to just pass in a list
    if len(names) is 1 and type(names[0]) not in (str, unicode):
        names = names[0]

    # Complain if no names passed in at all
    if not names:
        raise Exception("Need atleast one name to inject the object into")

    # Inject!
    sys.meta_path.append(FileFaker(names, obj))

class FileFaker(object):
    """
        Object to trick the import process to return specified value
        Rather than loading from a file
    """
    def __init__(self, names, value):
        self.names = names
        self._value = value

    def find_module(self, fullname, path=None):
        """Return self if trying to import one of the names we are masquerading"""
        if fullname in self.names:
            return self

    def load_module(self, fullname):
        """Create and return a module"""
        path, filename = self.path_from_fullname(fullname)

        # Get the existing module or create a new one (for reload to work)
        module = sys.modules.setdefault(fullname, imp.new_module(fullname))
        module.__file__ = os.path.join(path, '%s.py' % filename)
        module.__loader__ = self

        # Populate the module namespace with the injected attributes
        vals = self.value
        if type(vals) is dict:
            module.__dict__.update(vals)
        else:
            module.__dict__['value'] = vals

        return module

    @property
    def value(self):
        """
            Get a value from the one on on the class
            If it is callable, call it first
            Then normalize it with self.normalize_value
        """
        value = self._value
        if callable(value):
            value = value()
        return self.normalize_value(value)

    def normalize_value(self, value):
        """
            If the argument is a module:
                return the module's dictionary filtered by the module's __all__ attribute
            otherwise:
                return the argument as-is.

            If the module doesn't have an __all__ attribute
            , use all the attributes that don't begin with a double underscore.
        """
        if isinstance(value, types.ModuleType):
            if hasattr(value, '__all__'):
                keys = value.__all__
            else:
                key_filter = lambda k: not k.startswith('__')
                keys = filter(key_filter, value.__dict__.keys())

            # Make a dictionary from the keys we care about
            value = {key:getattr(value, key) for key in keys}

        return value

    def path_from_fullname(self, fullname):
        """Get path and filename from looking at the fullname used to import this module"""
        if '.' not in fullname:
            return '', fullname

        # Was a dot, we have path info to get
        path = ''
        package, filename = fullname.rsplit('.', 1)
        if package in sys.modules and hasattr(sys.modules[package], '__path__'):
            path = sys.modules[package].__path__[0]
        return path, filename

########################
###   FAILED IMPORTS
########################

def install_failed_import_handler():
    """
        Custom __import__ function that records failed imports
        Useful if say you're using werkzeug auto reloader
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

    # Make sure we don't override our custom handler
    if __builtin__.__import__.__name__ == '__import__':
        __builtin__.__import__ = new_import
