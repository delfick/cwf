from section import Section, Options, Values

S = Section
O = Options
V = Values

def init(package, name=None):
    if not name:
        name = package.split('.')[-1]
        
    sect = S('', name, None).base(
           module = '%s.views' % package
         , showBase = False
         , alias = name.capitalize()
         )
    
    return sect
