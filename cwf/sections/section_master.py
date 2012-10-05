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
        self.memoized = make_memoizer(self
            , 'admin', 'url_parts', 'active', 'exists', 'display', 'selected'
            )()

    ########################
    ###   MEMOIZED VALUES
    ########################

    def url_parts_value(self, section):
        '''Determine list of url parts of parent and this section'''
        urls = []
        if not section:
            return []

        if hasattr(section, 'parent') and section.parent:
            urls.extend(self.memoized.url_parts(section.parent))

        url = section.url
        if type(url) in (str, unicode) and url.startswith("/"):
            url = url[1:]

        if not urls or urls[-1] != '' or url != '':
            urls.append(url)

        if not urls or urls[0] != '':
            urls.insert(0, '')

        return urls

    def admin_value(self, section):
        '''Determine if section is only seen via admin priveleges'''
        if hasattr(section, 'parent') and section.parent:
            if self.memoized.admin(section.parent):
                return True

        is_admin = section.options.conditional('admin', self.request)
        return section.options.needs_auth or is_admin

    def active_value(self, section):
        '''Determine if section and parent are active'''
        if hasattr(section, 'parent') and section.parent:
            if not self.memoized.active(section.parent):
                return False
        return section.options.conditional('active', self.request)

    def exists_value(self, section):
        '''Determine if section and parent exists'''
        if hasattr(section, 'parent') and section.parent:
            if not self.memoized.exists(section.parent):
                return False
        return section.options.conditional('exists', self.request)

    def display_value(self, section):
        '''Determine if section and parent can be displayed'''
        if hasattr(section, 'parent') and section.parent:
            display, propogate = self.memoized.display(section.parent)
            if not display and propogate:
                return False, True
        return section.can_display(self.request)

    def selected_value(self, section, path):
        """Return True and rest of path if selected else False and no path."""
        url = section.url
        if not path and url == '':
            # No path and section is base
            return True, []

        # Make sure that regardless of what this section is, it's parent is selected
        # Also get here the rest of the path to check this section against
        parent_selected = True
        if section.parent:
            parent_selected, path = self.memoized.selected(section.parent, path=path)

        if parent_selected and not path and url == '':
            # Parent consumed the rest of the path
            # And this section is base
            return True, []

        # If the parent is selected or we have no path left
        # Then obviously no match
        if not parent_selected or not path:
            return False, []

        # Check against the url
        if path[0] == '' and unicode(url) in ('', '/'):
            return True, path[1:]
        elif path[0].lower() == unicode(url).lower():
            return True, path[1:]
        else:
            if section.options.promote_children:
                return True, path
            else:
                return False, []

    ########################
    ###   INFO
    ########################

    def iter_section(self, section, include_as, path):
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
            # We determine the parent url parts to give to the values
            parent_url_definition = self.memoized.url_parts(section.parent)
            parent_url_parts = []

            for index in range(len(parent_url_definition)):
                parent_url_parts.append(path[index])

            # Get the values!
            for url, alias in section.options.values.get_info(self.request, parent_url_parts, path):
                yield url, alias
        else:
            # This item only has one item to show in the menu
            url = section.url
            if include_as:
                url = include_as
            yield url, section.alias

    def get_info(self, section, include_as, path, parent=None):
        '''
            Yield Info objects for this section
            Used by templates to render the menus
        '''
        for url, alias in self.iter_section(section, include_as, path):
            for info in self._get_info(url, alias, section, path, parent):
                yield info

    def _get_info(self, url, alias, section, path, parent):
        """Closure to yield info for a url, alias pair"""
        info = Info(url, alias, section, parent)
        path_copy = list(path)

        # Use SectionMaster logic to keep track of parent_url and parent_selected
        # By giving it the info instead of section
        admin = lambda : self.memoized.admin(info)
        appear = lambda : self.memoized.exists(info) and self.memoized.active(info)
        display = lambda : self.memoized.display(info)[0]
        selected = lambda : self.memoized.selected(info, path=path_copy)
        url_parts = lambda: self.memoized.url_parts(info)

        # Give lazily loaded stuff to info and yield it
        info.setup(admin, appear, display, selected, url_parts)
        yield info

########################
###   INFO OBJECT
########################

class Info(object):
    '''Object to hold information used by templates'''
    def __init__(self, url, alias, section, parent):
        self.url = url
        self.alias = alias
        self.parent = parent or section.parent
        self.section = section
        self.options = section.options

    def setup(self, admin, appear, display, selected, url_parts):
        self.admin = admin
        self.appear = appear
        self.display = display
        self.selected = selected
        self.url_parts = url_parts

    def setup_children(self, children, has_children):
        self.children = children
        self.has_children = has_children

    def can_display(self, request):
        return self.section.can_display(request)

    @property
    def menu_children(self):
        return self.section.menu_children

    @property
    def full_url(self):
        return '/'.join(str(p) for p in self.url_parts()) or '/'

    def __repr__(self):
        return '<Info %s:%s>' % (self.url, self.alias)
