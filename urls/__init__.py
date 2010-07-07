from section import Section, Options, Values, Menu

S = Section
O = Options
V = Values

def init(self, package, name=None):
    sect = S('', name, None).base(
           module = package
         , showBase = False
         )
    
    return sect
