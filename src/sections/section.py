from django.conf.urls.defaults import include, patterns
from django.http import Http404

from errors import ConfigurationError
from dispatch import dispatcher

########################
###
###   SECTION
###
########################

class Section(object):
    '''
        Contain logic for each section of the url
    '''
    def __init__(self, url='/', name=None, parent=None):
        self.url  = url
        self.name = name
        self.parent = parent
        
        self._base = None
        self._children = []
        
        self._pattern = None
        self._options = None
        if hasattr(self, 'setup'):
            if callable(self.setup):    
                self.setup()
        
    ########################
    ###   USAGE
    ########################
    
    def add(self, url, match=None, name=None):
        """Adds a child to self.children"""
        if not url:
            raise ConfigurationError("Use section.first() to add a section with same url as parent")
        
        section = Section(url=url, name=name, parent=self)
        section.options = self.options.clone(match=match)
        self.add_child(section)
        
        return section

    def first(self, url="", match=None, name=None):
        """Adds a child with the same url as the parent as self.base"""
        if name is None:
            name = self.name
        
        section = Section(url=url, name=name, parent=self)
        section.options = self.options.clone(match=match)
        self.add_child(section, first=True)
        
        return section
        
    def base(self, *args, **kwargs):
        """
            Extends self.options with the given keywords.
            It also accepts positional arguements but doesn't use them.
            This is purely so I can use it like this
            section.add('asdf').baes(''
                , kw1 = value1
                , kw2 = value2
                , kw3 = value3
                )
            Without the positional argument at the beginning, the first line can't have a comma
        """
        self.options.set_everything(**kwargs)
        return self
    
    def adopt(self, *sections, **kwargs):
        '''
            Adopt zero or more sections as it's own
            Will also replace this section's parent with itself
            If clone is specified as a keyword argument to be True, then sections will be cloned
            Otherwise, sections will just have their parent overriden
        '''
        clone = kwargs.get('clone')
        for section in sections:
            if clone:
                section = section.clone(parent=self)
            else:
                section.parent = self
            
            self.add_child(section)
        
        return self
    
    def merge(self, section, take_base=False):
        '''
            Copy children from a section into this section.
            Will only replace self._base if take_base is True
        '''
        if take_base and section._base:
            if section._base:
                self._base = section._base.clone(parent=self)
            else:
                self._base = None
        
        self._children = [child.clone(parent=self) for child in section._children]
        return self
    
    def copy(self, section):
        """Create a copy of the given section and add as a child"""
        section = section.clone(parent=section)
        self.add_child(section)
        return section
    
    def add_child(self, section, first=False):
        if first:
            self._base = section
        else:
            self._children.append(section)
        
    ########################
    ###   SPECIAL
    ########################
    
    @property
    def options(self):
        if not self._options:
            self._options = Options()
        return self._options
    
    @options.setter
    def options(self, val):
        self._options = val
    
    @property
    def alias(self):
        alias = self.options.alias
        if not alias and self.url:
            alias = self.url.capitalize()
        return alias
    
    @property
    def children(self):
        if self._base:
            yield self._base
        
        for child in self._children:
            yield child
    
    def __iter__(self):
        """Return self followed by all children"""
        yield self
        for section in self.children:
            for sect in section:
                yield sect
    
    def __unicode__(self):
        if self.name:
            return "<CWF Section %s>" % '%s : %s' % (self.name, self.url)
        else:
            return "<CWF Section %s>" % self.url

    def __repr__(self):
        return unicode(self)
        
    ########################
    ###   URL PATTERNS
    ########################

    def patterns(self, **kwargs):
        """
            Return patterns object for this section
            A django patterns object
                with (pattern, view, kwarg, name) tuples for the section and it's children
            Each pattern will only go up the parent chain untill no parent or section is stop_at
        """
        yield patterns('', *list(self.pattern_list(**kwargs)))
    
    def include_patterns(self, namespace, app_name, include_as=None):
        """
            Return patterns object for this section using an include
            Equivelant to:
                (path, include(patterns(children_only=True, stop_at=self, start=False), namespace, app_name))
            
            Where path is determined by self.include_path(include_as)
        """
        path = self.include_path(include_as)
        includer = include(self.patterns(children_only=True, stop_at=self), namespace, app_name)
        return (path, includer)
        
    def pattern_list(self, children_only=False, stop_at=None, start=True):
        """Return list of url patterns for this section and its children"""
        if self.options.promote_children or not self.children:
            # If not showing base, then there is no direct url to that section
            # But the children will respect the part of the url that belongs to this section
            pattern = self.url_pattern(stop_at, start=start)
            view, kwargs = self.options.url_view(self)
            yield (pattern, view, kwargs, self.name)
        
        # Yield children
        for child in self.children:
            for url_pattern in child.pattern_list(stop_at, start=start):
                yield url_pattern
        
    ########################
    ###   URL UTILITY
    ########################
    
    def url_pattern(self, stop_at=None, end=None):
        """Get tuple to be used for url pattern for this section"""
        url_parts = self.determine_url_parts(stop_at)
        return self.options.create_pattern(url_parts, end=end)
        
    def include_path(self, include_as=None):
        """
            Determine path to this includer
            Will use self.url_pattern without trailing $
            unless include_as is specified which will override this
        """
        if include_as:
            while include_as.endswith("/"):
                include_as = include_as[:-1]
            return "^%s/" % include_as
        
        # No include_as specified
        return self.url_pattern(stop_at=self, end=False, start=False)

    def determine_url_parts(self, stop_at=None):
        """Get list of patterns making the full pattern for this section"""
        if not self._url_parts:
            url_parts = []
            if self.parent and not self is stop_at:
                # Get parent patterns
                url_parts = list(self.parent.determine_url_parts(stop_at))
            
            match = self.options.match
            if match:
                url_parts.append("(?P<%s>%s)" % (match, self.url))
            else:
                url_parts.append(self.url)
            
            self._url_parts = url_parts
        return self._url_parts
        
    ########################
    ###   UTILITY
    ########################
    
    def clone(self, **kwargs):
        """
            Create a clone of this section
            Will keep references to old children, but not clone them
        """
        for attr in ('url', 'name', 'parent'):
            if attr not in kwargs:
                kwargs[attr] = getattr(self, attr)
        new = Section(**kwargs)
        new.options = self.options.clone(all=True)
        return new
    
    def rootAncestor(self):
        """Find ancestor that has no parent"""
        result = self
        while result.parent:
            parent = result.parent
        return result
    
    def reachable(self, request):
        """Determine if this view is reachable for this request"""
        if self.parent and not self.parent.reachable(request):
            return False
        return self.options.reachable(request)
        
########################
###   SECTION MASTER
########################

class SectionMaster(object):
    '''Memoize values for sections for a given request'''
    def __init__(self, request):
        self.request = request
        self.results = {'url_parts' : {}, 'show':{}, 'exists':{}, 'display':{}, 'selected':{}}
    
    ########################
    ###   MEMOIZED DISPLAY, SHOW, EXISTS
    ########################
    
    def memoizer(name):
        '''Return function that uses memoized for particular type'''
        def memoized(self, section):
            return self.memoized(name, section)
        return memoized
    
    show = property(memoizer('display'))
    exists = property(memoizer('display'))
    display = property(memoizer('display'))
    selected = property(memoizer('selected'))
    url_parts = property(memoizer('url_parts'))
    
    def memoized(self, typ, section, **kwargs):
        identity = id(section)
        if identity not in self.results[typ]:
            self.results[typ][identity] = getattr(self, "%s_value" % typ)(section, **kwargs)
        return self.results[typ][identity]
        
    ########################
    ###   VALES FOR DISPLAY, SHOW, EXISTS
    ########################
    
    def url_value(self, section):
        '''Determine list of url parts of parent and this section'''
        urls = []
        if section.parent:
            urls.extend(self.url(section.parent))
        
        url = section.url
        if url.startswith("/"):
            url = url[1:]
        
        urls.append(url)
        if urls[0] != '':
            urls.insert(0, '')
        
        return urls
    
    def show_value(self, section):
        '''Determine if section and parent can be shown'''
        if section.parent and not self.show(section.parent):
            return False
        return section.options.show(request)
    
    def display_value(self, section):
        '''Determine if section and parent can be displayed'''
        if section.parent and not self.display(section.parent):
            return False
        return section.options.display(request)
    
    def exists_value(self, section):
        '''Determine if section and parent exists'''
        if section.parent and not self.exists(section.parent):
            return False
        return section.options.exists(request)
    
    def selected_value(self, section, request, path):
        """Return True and rest of path if selected else False and no path."""
        url = section.url
        parentSelected = not section.parent or self.selected(section.parent)
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
            appear = lambda: self.exists(info) and self.display(info) and self.show(info)
            selected = lambda: self.selected(info, request=request, path=path)
            url_parts = lambda: self.url_parts(info)
            
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
