from section import Section, Options, Values

S = Section
O = Options
V = Values

def init(package, name=None, kls='views', target='base'):
    if not name:
        name = package.split('.')[-1]
        
    sect = S('', name, None).base(''
         , module = '%s.views' % package
         , kls = kls
         , target = target
         , showBase = False
         , alias = name.capitalize()
         )
    
    return sect
