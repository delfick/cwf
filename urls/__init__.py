from section import Section, Options, Values

S = Section
O = Options
V = Values

def init(package, name=None):
    sect = S('', name, None).base(
           module = '%s.views' % package
         , showBase = False
         )
    
    return sect
