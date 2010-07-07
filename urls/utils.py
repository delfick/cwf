def iterSects(sections, activeOnly=True):
    def _iter():
        for sect in sections:
            options = {}
            if type(sect) is tuple:
                if len(sect) == 2:
                    sect, options = sect
                else:
                    sect = sect[0]
            
            active = options.get('active', True)
            
            if active or not activeOnly:
                yield sect, options
    
    return _iter
