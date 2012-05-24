from django.conf.urls.defaults import include, patterns

from errors import ConfigurationError
from dispatch import dispatcher
from options import Options

########################
###   SECTION
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
        
    ########################
    ###   USAGE
    ########################
    
    def add(self, url, match=None, name=None):
        """Adds a child to self.children"""
        if not url:
            raise ConfigurationError("Use section.first() to add a section with same url as parent")
        
        section = self.make_section(url, match, name)
        self.add_child(section)
        return section

    def first(self, url="", match=None, name=None):
        """Adds a child with the same url as the parent as self._base"""
        if name is None:
            name = self.name
        
        section = self.make_section(url, match, name)
        self.add_child(section, first=True)
        return section
        
    def configure(self, **kwargs):
        """
            Extends self.options with the given keywords.
            It also accepts positional arguments but doesn't use them.
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
        
    ########################
    ###   SECTION ADDERS
    ########################
    
    def make_section(self, url, match, name):
        """
            Create a new section based on current one
            * Gives new section parent of this
            * Gives it provided url and name
            * Gives new section clone of this section's options with match overridden
        """
        section = Section(url=url, name=name, parent=self)
        section.options = self.options.clone(match=match)
        return section
    
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
        if take_base:
            if section._base:
                self._base = section._base.clone(parent=self)
            else:
                self._base = None
        
        for child, consider_for_menu in section._children:
            self.add_child(child.clone(parent=self), consider_for_menu=consider_for_menu)
        
        return self
    
    def copy(self, section):
        """Create a copy of the given section and add as a child"""
        section = section.clone(parent=self)
        self.add_child(section)
        return self
    
    def add_child(self, section, first=False, consider_for_menu=True):
        """Add a child to the section"""
        if first:
            self._base = (section, consider_for_menu)
        else:
            self._children.append((section, consider_for_menu))
        
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
        """
            Get all the children
            Children are from self._base and self._children.
            All children are a tuple of (child, consider_for_menu)
        """
        if self._base:
            yield self._base[0]
        
        for child, _ in self._children:
            yield child
    
    @property
    def menu_sections(self):
        """
            Get all the children that are considered for the menu
            Children are from self._base and self._children.
            All children are a tuple of (child, consider_for_menu)
            Yield only those whose consider_for_menu is truthy
        """
        if self._base and self._base[1]:
            yield self._base[0]
        
        for child, consider_for_menu in self._children:
            if consider_for_menu:
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
        if not self.options.promote_children or not self.children:
            yield self.pattern_list_first(stop_at, start)
        
        # Yield children
        for child in self.children:
            for url_pattern in child.pattern_list(stop_at, start=start):
                yield url_pattern
        
    def pattern_list_first(self, stop_at, start):
        """Yield pattern list for this section"""
        pattern = self.url_pattern(stop_at, start=start)
        view, kwargs = self.options.url_view(self)
        return (pattern, view, kwargs, self.name)
        
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
            while include_as.startswith("^"):
                include_as = include_as[1:]
            
            while include_as.endswith("/"):
                include_as = include_as[:-1]
            
            return "^%s/" % include_as
        
        # No include_as specified
        return self.url_pattern(stop_at=self, end=False, start=False)

    def determine_url_parts(self, stop_at=None):
        """Get list of patterns making the full pattern for this section"""
        if not hasattr(self, '_url_parts'):
            url_parts = self.parent_url_parts(stop_at)
            url_parts.append(self.own_url_part())
            self._url_parts = url_parts
        return self._url_parts    
    
    def parent_url_parts(self, stop_at):
        """Get url_parts from parent"""
        parts = []
        if self.parent and not self is stop_at:
            # Get parent patterns
            parts = list(self.parent.determine_url_parts(stop_at))
        return parts
    
    def own_url_part(self):
        """Get url part for this section"""
        part = self.url
        match = self.options.match
        if match:
            part = "(?P<%s>%s)" % (match, self.url)
        
        return part
        
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
        parents = []
        while result.parent and result.parent not in parents:
            parents.append(result.parent)
            result = result.parent
        return result
    
    def reachable(self, request):
        """Determine if this view is reachable for this request"""
        if self.parent and not self.parent.reachable(request):
            return False
        return self.options.reachable(request)
