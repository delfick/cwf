from section import Section
from options import Options
from values import Values

S = Section
O = Options
V = Values

def init(package, name=None, kls='views'):
    """
        Helper to create a Section object with defaults for module and kls
        Use like section = init(__package__)
    """
    if not name:
        name = package.split('.')[-1]
    alias = name.capitalize()

    return S('', name).configure(''
         , kls = kls
         , alias = alias
         , module = '%s.views' % package
         )
