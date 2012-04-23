########################
###   MEMOIZER
########################

def memoized(self, typ, obj, **kwargs):
    """
        For a given typ:
            Determine identity of obj
                Memoize result of self.calculator.<typ>_value(obj, **kwargs)
    """
    identity = id(obj)
    if identity not in self.results[typ]:
        self.results[typ][identity] = getattr(self.calculator, "%s_value" % typ)(obj, **kwargs)
    return self.results[typ][identity]

def memoizer(typ):
    '''Return function that uses memoized for particular type'''
    def memoized(self, obj):
        return self.memoized(typ, obj)
    return memoized

def make_memoizer(calculator, *namespaces):
    '''
        Create a class for memoizing particular values under particular namespaces
        Will use <typ>_value(obj, **kwargs) methods on calculator to memoize results for an obj
        Where identity of obj is determined by id(obj)
    '''
    attrs = {}
    results = {}
    for value in values:
        results[value] = {}
        attrs[value] = property(memoizer(value))
    
    attrs['memoized'] = memoized
    attrs['calculator'] = calculator
    
    return type("Memoizer", (object, ), attrs)

########################
###   SECTION MASTER
########################

class SectionMaster(object):
    '''Determine information for sections for a given request'''
    def __init__(self, request):
        self.request = request
        self.memoized = make_memoizer(self, 'url_parts', 'show', 'exists', 'display', 'selected')
        
    ########################
    ###   MEMOIZED VALUES
    ########################
    
    def url_parts_value(self, section):
        '''Determine list of url parts of parent and this section'''
        urls = []
        if section.parent:
            urls.extend(self.memoized.url_parts(section.parent))
        
        url = section.url
        if url.startswith("/"):
            url = url[1:]
        
        urls.append(url)
        if urls[0] != '':
            urls.insert(0, '')
        
        return urls
    
    def show_value(self, section):
        '''Determine if section and parent can be shown'''
        if section.parent and not self.memoized.show(section.parent):
            return False
        return section.options.show(request)
    
    def display_value(self, section):
        '''Determine if section and parent can be displayed'''
        if section.parent and not self.memoized.display(section.parent):
            return False
        return section.options.display(request)
    
    def exists_value(self, section):
        '''Determine if section and parent exists'''
        if section.parent and not self.memoized.exists(section.parent):
            return False
        return section.options.exists(request)
    
    def selected_value(self, section, request, path):
        """Return True and rest of path if selected else False and no path."""
        url = section.url
        parentSelected = not section.parent or self.memoized.selected(section.parent)
        if not parentSelected or not path:
            return False, []
        
        if not self.options.conditional('show_base', request):
            return True, path
        
        # We have path and url
        if path[0] == '' and url == '/':
            selected = True
        else:
            selected = path[0].lower() == str(url).lower()
        
        if not selected:
            return False, []
        
        # Only return remaining path if this section is selected
        return selected, path[1:]
        
    ########################
    ###   INFO
    ########################
    
    def get_info(self, request, section, path, parent=None, gen=None):
        '''
            Yield Info objects for this section
            Used by templates to render the menus
        '''
        if not section.options.conditional('active', request):
            # Section not even active
            return
        
        def iter_info():
            if section.options.values():
                # This section has multiple items to show in the menu
                parent_url_parts = self.url_parts(parent)
                for url, alias in section.options.values.get_info(request, section, path, parent_url_parts):
                    yield url, alias
            else:
                # This item only has one item to show in the menu
                yield self.url, self.alias
        
        for url, alias in iter_info():
            info = Info(url, alias, section, parent)
            
            # Use SectionMaster logic to keep track of parent_url and parent_selected
            # By giving it the info instead of section
            appear = lambda: self.memoized.exists(info) and self.memoized.display(info) and self.memoized.show(info)
            selected = lambda: self.memoized.selected(info, request=request, path=path)
            url_parts = lambda: self.memoized.url_parts(info)
            
            # Give lazily loaded stuff to info and yield it
            info.setup(appear, selected, url_parts)
            yield info
        
########################
###   INFO OBJECT
########################

class Info(object):
    '''Object to hold information used by templates'''
    def __init__(self, url, alias, section, parent):
        self.url = url
        self.alias = alias
        self.parent = parent
        self.section = section
    
    def setup(self, appear, selected, url_parts):
        self.appear = appear
        self.selected = selected
        self.url_parts = url_parts
