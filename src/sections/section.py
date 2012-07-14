from django.conf.urls.defaults import include, patterns
from django.http import Http404
from functools import wraps

from errors import ConfigurationError
from pattern_list import PatternList
from dispatch import dispatcher
from options import Options

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
        """Creates a new section and uses add_child to add it as a child"""
        if not url:
            raise ConfigurationError("Use section.first() to add a section with same url as parent")
        
        section = self.make_section(url, match, name)
        self.add_child(section)
        return section

    def first(self, url="", match=None, name=None):
        """Creates a new section and adds it as a base with add_child(first=True)"""
        if name is None:
            name = self.name
        
        section = self.make_section(url, match, name)
        self.add_child(section, first=True)
        return section
        
    def configure(self, *_, **kwargs):
        """
            Extends self.options with the given keywords.
            It also accepts positional arguments but doesn't use them.
            This is purely so I can use it like this
            section.add('asdf').configure(''
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
            
            If clone is specified as a keyword argument to be True then section is copied
            Otherwise, sections will just have their parent overriden and added as a child
        '''
        clone = kwargs.get('clone')
        for section in sections:
            if clone:
                self.copy(section, consider_for_menu=kwargs.get("consider_for_menu"))
            else:
                section.parent=self
                self.add_child(section, consider_for_menu=kwargs.get("consider_for_menu"))
        
        return self
    
    def merge(self, section, take_base=False):
        '''
            Copy children from a section into this section.
            Will only copy section._base if take_base is True
        '''
        if take_base and hasattr(section, '_base') and section._base:
            base, consider_for_menu = section._base
            self.copy(base, first=True, consider_for_menu=consider_for_menu)
        
        for child, consider_for_menu in section._children:
            self.copy(child, consider_for_menu=consider_for_menu)
        
        return self
    
    def copy(self, section, first=False, consider_for_menu=None):
        """Create a clone of the given section, merge clone with original; and add clone as a child"""
        cloned = section.clone(parent=self)
        self.add_child(cloned, first=first, consider_for_menu=consider_for_menu)
        cloned.merge(section, take_base=True)
        return self
    
    def add_child(self, section, first=False, consider_for_menu=True):
        """
            Add a child to the section
            If first, then overwrite _base, otherwise add to _children.

            Will be appended as a tuple (children, consider_for_menu)
        """
        if first:
            self._base = (section, consider_for_menu)
        else:
            self._children.append((section, consider_for_menu))
        return section
        
    ########################
    ###   SPECIAL
    ########################
    
    @property
    def options(self):
        """Options is a lazily loaded Options object"""
        if not self._options:
            self._options = Options()
        return self._options
    
    @options.setter
    def options(self, val):
        """Setter to not lazily load Options object if we already have an object to use"""
        self._options = val

    @property
    def url_options(self):
        """
            Get url options for this section.
            If the section has a base, then use options on that
            Otherwise just use options on the section itself
        """
        if hasattr(self, '_base') and self._base:
            base, _ = self._base
            return base.options
        else:
            return self.options
    
    @property
    def alias(self):
        """
            Either alias on the options
            or just capitalized url
        """
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
    def url_children(self):
        """
            Yield all children followed by self
            This ensures longer urls are specified before shorter urls
        """
        for child in self.children:
            yield child
        yield self
    
    @property
    def menu_sections(self):
        """
            Get all the children that are considered for the menu
            Children are from self._base and self._children.
            All children are a tuple of (child, consider_for_menu)
            Yield only those whose consider_for_menu is truthy
        """
        if self._base and self._base[1]:
            for promoted in self._base[0].promoted_menu_children:
                yield promoted
        
        for child, consider_for_menu in self._children:
            if consider_for_menu:
                for promoted in child.promoted_menu_children:
                    yield promoted

    @property
    def promoted_menu_children(self):
        """
            Used to get any promoted children when calculating menu_sections
            And recurse into promoted children of those promoted children
            If no promoted children, just yield self
        """
        if not self.options.promote_children:
            yield self
        else:
            for child in self.menu_sections:
                for promoted in child.promoted_menu_children:
                    yield promoted
    
    @property
    def has_children(self):
        """Return whether section has children"""
        return bool(any(self.children))
    
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

    def patterns(self):
        """
            Return patterns object for this section
            A django patterns object
                with (pattern, view, kwarg, name) tuples for the section and it's children
        """
        result = []
        for section, (pattern, view, kwarg, name) in PatternList(self):
            view = self.make_view(view, section)
            urls = patterns('', (pattern, view, kwarg, name))
            result.extend(urls)
        return result
    
    def include_patterns(self, namespace, app_name, include_as=None, start=False, end=False):
        """
            Return patterns object for this section using an include
            Equivalent to:
                (path, include(patterns(), namespace, app_name))
            
            Where path is determined by self.include_path(include_as, start, end)
        """
        path = PatternList(self).include_path(include_as, start, end)
        includer = include(self.patterns(), namespace, app_name)
        return (path, includer)

    def make_view(self, view, section):
        """
            Wrap view for a pattern:
             * Set section on requeset
             * Make sure that the section is reachable
             * If section isn't reachable, raise Http404
        """
        @wraps(view)
        def view_wrap(request, *args, **kwargs):
            request.section = section
            if section and not section.reachable(request):
                raise Http404
            return view(request, *args, **kwargs)
        return view_wrap
    
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
    
    def root_ancestor(self):
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
