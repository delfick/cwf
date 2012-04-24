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
    def memoized(self, obj, **kwargs):
        return self.memoized(typ, obj, **kwargs)
    return memoized

def make_memoizer(calculator, *namespaces):
    '''
        Create a class for memoizing particular values under particular namespaces
        Will use <typ>_value(obj, **kwargs) methods on calculator to memoize results for an obj
        Where identity of obj is determined by id(obj)
    '''
    attrs = {}
    results = {}
    for value in namespaces:
        results[value] = {}
        attrs[value] = memoizer(value)
    
    attrs['results'] = results
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
        self.memoized = make_memoizer(self, 'url_parts', 'show', 'exists', 'display', 'selected')()
        
    ########################
    ###   MEMOIZED VALUES
    ########################
    
    def url_parts_value(self, section):
        '''Determine list of url parts of parent and this section'''
        urls = []
        if not section:
            return []
        
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
        return section.options.show(self.request)
    
    def display_value(self, section):
        '''Determine if section and parent can be displayed'''
        if section.parent and not self.memoized.display(section.parent):
            return False
        return section.options.display(self.request)
    
    def exists_value(self, section):
        '''Determine if section and parent exists'''
        if section.parent and not self.memoized.exists(section.parent):
            return False
        return section.options.exists(self.request)
    
    def selected_value(self, section, path):
        """Return True and rest of path if selected else False and no path."""
        url = section.url
        parentSelected = not section.parent or self.memoized.selected(section.parent)
        if not parentSelected or not path:
            return False, []
        
        if section.options.conditional('promote_children', self.request):
            return True, path
        
        if (path[0] == '' and url == '/') or (path[0].lower() == str(url).lower()):
            return True, path[1:]
        else:
            return False, []
        
    ########################
    ###   INFO
    ########################

    def iter_section(self, section, path):
        """
            Yield (url, alias) pairs for this section
            If section isn't active, nothing is yielded
            If section has values, url, alias is yielded for each value
            if Section has no values, it's own url and alias is yielded
        """
        if not section.options.conditional('active', self.request):
            # Section not even active
            return
        
        if section.options.values:
            # This section has multiple items to show in the menu
            parent_url_parts = self.memoized.url_parts(section.parent)
            for url, alias in section.options.values.get_info(self.request, path, parent_url_parts):
                yield url, alias
        else:
            # This item only has one item to show in the menu
            yield section.url, section.alias
    
    def get_info(self, section, path):
        '''
            Yield Info objects for this section
            Used by templates to render the menus
        '''
        for url, alias in self.iter_section(section, path):
            info = Info(url, alias, section)
            path_copy = list(path)
            
            # Use SectionMaster logic to keep track of parent_url and parent_selected
            # By giving it the info instead of section
            appear = lambda : self.memoized.exists(info) and self.memoized.display(info) and self.memoized.show(info)
            selected = lambda: self.memoized.selected(info, path=path_copy)
            url_parts = lambda: self.memoized.url_parts(info)
            
            # Give lazily loaded stuff to info and yield it
            info.setup(appear, selected, url_parts)
            yield info

########################
###   INFO OBJECT
########################

class Info(object):
    '''Object to hold information used by templates'''
    def __init__(self, url, alias, section):
        self.url = url
        self.alias = alias
        self.section = section
    
    def setup(self, appear, selected, url_parts):
        self.appear = appear
        self.selected = selected
        self.url_parts = url_parts
