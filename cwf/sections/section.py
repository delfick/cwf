from django.conf.urls.defaults import patterns as django_patterns
from django.http import Http404
from functools import wraps

from errors import ConfigurationError
from pattern_list import PatternList
from dispatch import dispatcher
from options import Options

class Item(object):
    """
        Data structure to represent an item in the menu
    """
    def __init__(self, section, consider_for_menu=True, include_as=None):
        self.section = section
        self.include_as = include_as
        self.consider_for_menu = consider_for_menu

    @classmethod
    def create(cls, section, kwargs):
        options = {key:val for key, val in kwargs.items() if key in ('consider_for_menu', 'include_as')}
        return cls(section, **options)

    def clone(self, parent):
        """Convenience for making a clone of this item"""
        old_section = self.section
        cloned_section = old_section.clone(parent=parent)
        cloned_section.merge(old_section, take_base=True)
        return self.__class__(cloned_section, consider_for_menu=self.consider_for_menu, include_as=self.include_as)

    def __repr__(self):
        return "<Item {}|:|menu:{}|:|include:{}>".format(self.section, self.consider_for_menu, self.include_as)

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

    def add(self, url, match=None, name=None, first=False):
        """Creates a new section and uses add_child to add it as a child"""
        if not url:
            raise ConfigurationError("Use section.first() to add a section with same url as parent")

        section = self.make_section(url, match, name)
        self.add_child(section, first=first)
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

    def adopt(self, *sections, **options):
        '''
            Adopt zero or more sections as it's own
            Will also replace this section's parent with itself

            If clone is specified as a keyword argument to be True then section is copied
            Otherwise, sections will just have their parent overriden and added as a child
        '''
        clone = False
        if 'clone' in options:
            clone = options['clone']
            del options['clone']

        for section in sections:
            if clone:
                self.copy(section, **options)
            else:
                section.parent=self
                self.add_child(section, **options)

        return self

    def merge(self, section, take_base=False):
        '''
            Copy children from a section into this section.
            Will only copy section._base if take_base is True
        '''
        if take_base and section._base:
            self._base = section._base.clone(parent=self)

        for item in section._children:
            self._children.append(item.clone(parent=self))

        return self

    def add_child(self, section, first=False, **options):
        """
            Add a child to the section
            If first, then overwrite _base, otherwise add to _children.

            Will be appended as an instance of the Item object
        """
        new_item = Item.create(section, options)
        if first:
            self._base = new_item
        else:
            self._children.append(new_item)
        return section

    def copy(self, section, first=False, **kwargs):
        """Create a clone of the given section, merge clone with original; and add clone as a child"""
        options = {key:val for key, val in kwargs.items() if key in ('consider_for_menu', 'include_as')}

        cloned = section.clone(parent=self)
        self.add_child(cloned, first=first, **options)
        cloned.merge(section, take_base=True)
        return self

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
        if self._base:
            return self._base.section.options
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
        """
        if self._base:
            yield self._base

        for item in self._children:
            yield item

    @property
    def url_children(self):
        """
            Yield all children followed by self
            This ensures longer urls are specified before shorter urls
        """
        for item in self.children:
            yield item
        if not self._base:
            yield Item(self)

    @property
    def menu_children(self):
        """
            Get all the children that are considered for the menu
            Children are from self._base and self._children.
            Yield only those whose consider_for_menu is truthy
        """
        if self._base and self._base.consider_for_menu:
            for promoted in self._base.section.promoted_menu_children(self._base):
                yield promoted

        for item in self._children:
            if item.consider_for_menu:
                for promoted in item.section.promoted_menu_children(item):
                    yield promoted

    def promoted_menu_children(self, item):
        """
            Used to get any promoted children when calculating menu_children
            And recurse into promoted children of those promoted children
            If no promoted children, just yield self
        """
        if not self.options.promote_children:
            yield item
        else:
            for item in self.menu_children:
                for promoted in item.section.promoted_menu_children(item):
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

    def patterns(self, without_include=False):
        """Get urlpatterns for this section"""
        tuples = list(PatternList(self, without_include=without_include))
        return django_patterns('', *tuples)

    def make_view(self, view, section):
        """
            Wrap view for a pattern:
             * Set section on request
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
            Will not transfer over references to children
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

    def can_display(self, request):
        """Determine if we can display this section"""
        options = self.options
        can_display = options.conditional('display', request)
        has_permissions = options.has_permissions(request.user)
        return has_permissions and can_display, options.propogate_display
