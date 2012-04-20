from django.conf.urls.defaults import include, patterns
from django.http import Http404

from dispatch import dispatch

from types import FunctionType
import re

regexes = {
    'multiSlash' : re.compile('/+'),
}

########################
###
###   SECTION
###
########################

class Section(object):
    def __init__(self, url='/', name=None, parent=None):
        self.url  = url
        self.name = name
        
        self.parent   = parent
        self._options = None
        self.children = []
        
        self._pattern  = None
        
        if hasattr(self, 'setup'):
            if callable(self.setup):    
                self.setup()
    
    def add(self, url, match=None, name=None):
        """Adds a child to self.children"""
        if url == '':
            raise ValueError("Use section.first() to add a section with same url as parent")
        
        section = Section(url=url, name=name, parent=self)
        section.options = self.options.clone(match=match)
        self.children.append(section)
        
        return section

    def first(self, url="", match=None, name=None):
        """Adds a child with the same url as the parent at the beginning of self.children"""
        if self.children and self.children[0].url == '':
            # Override if we already have a first section
            self.children.pop(0)
        
        if name is None:
            name = self.name
            
        section = Section(url=url, name=name, parent=self)
        section.options = self.options.clone(match=match)
        self.children.insert(0, section)
        
        return section
        
    def base(self, *args, **kwargs):
        """Extends self.options with the given keywords.
        It also accepts positional aguements but doesn't use them.
        This is purely so I can use it like this
        section.add('asdf').baes(''
            , kw1 = value1
            , kw2 = value2
            , kw3 = value3
            )
        Without the positional argument at the beginning, the first line can't have a comma
        """
        self.options.update(**kwargs)
        return self
    
    def adopt(self, *sections):
        for section in sections:
            section.parent = self
            self.children.append(section)
        
        return self
        
    ########################
    ###   SPECIAL
    ########################
    
    def _get_options(self):
        current = self._options
        if not current:
            opts = Options()
            self._options = opts
            return opts
        else:
            return current
    
    def _set_options(self, value):
        self._options = value
    
    options = property(_get_options, _set_options, None,
    """ Always want to have an options object
        To avoid creating one unecessarily, we lazily create it
    """)
            
    def __iter__(self):
        """Return self followed by all children"""
        yield self
        for section in self.children:
            for sect in section:
                yield sect
    
    def __unicode__(self):
        template = "<CWF Section %s>"
        if self.name:
            return template % '%s : %s' % (self.name, self.url)
        else:
            return template % self.url

    def __repr__(self):
        return unicode(self)
        
    ########################
    ###   UTILITY
    ########################
    
    def rootAncestor(self):
        """Recursively get ancestor that has no parent"""
        if self.parent:
            return self.parent.rootAncestor()
        else:
            return self
        
    def show(self, request=None):
        """Can only show if options say this section can show and parent can show"""
        parentShow = True
        if self.parent:
            parentShow = self.parent.show(request)
        
        if parentShow:
            return self.options.show(request)
        
        return False
        
    def appear(self, request=None):
        """Can only appear if allowed to be displayed and shown"""
        display = self.options.display
        adminOnly = False
        
        if callable(display):
            display = display(request)
        
        if type(display) is not bool:
            adminOnly, display = display
        
        if adminOnly:
            self.options.admin = True
        
        return display and self.show(request)
    
    def getInfo(self, path, parentUrl=None, parentSelected=True, gen=None, request=None):
        if self.options.active:
            def get(path, url=None):
                """Helper to get children, fullUrl and determine if selected"""
                if not url:
                    url = self.url
                
                if type(url) in (str, unicode) and url.startswith('/'):
                    url = url[1:]
                
                selected, path = self.determineSelection(path, parentSelected, url)
                
                if not parentUrl:
                    fullUrl = []
                else:
                    fullUrl = parentUrl[:]
                
                if url is not None:
                    if url != '' or len(fullUrl) == 0:
                        fullUrl.append(url)
                
                children = self.children
                if self.children:
                    if gen:
                        # Make it a lambda, so that template can remake the generator
                        # Generator determines how to deliver info about the children
                        children = lambda : gen(self.children, path, fullUrl, selected, request=request)
                
                # We want absolute paths
                if fullUrl and fullUrl[0] != '':
                    fullUrl.insert(0, '')
                
                return selected, children, fullUrl
            
            if parentUrl is None:
                parentUrl = []
            
            appear = lambda : self.appear(request)
            if self.options.needsAuth and not self.options.admin:
                self.options.admin = True
            
            if self.options.values:
                for alias, url in self.options.values.getInfo(parentUrl, path, request=request):
                    selected, children, fullUrl = get(path, url)
                    yield (self, appear, fullUrl, alias, selected, children, self.options)
            else:
                alias = self.getAlias()
                selected, children, fullUrl = get(path)
                yield (self, appear, fullUrl, alias, selected, children, self.options)
    
    def getAlias(self):
        alias = self.options.alias
        if not alias and self.url:
            alias = self.url.capitalize()
        return alias
        
    def determineSelection(self, path, parentSelected, url=None):
        """Return True and rest of path if selected else False and no path."""
        if not url:
            url = self.url
        
        if parentSelected and self.options.showBase == False and url == '':
            return True, path
        
        if not parentSelected or (not path and url != ''):
            return False, []
        else:
            if not path:
                # Must be a base address and its parent is selected
                return True, []
            
            selected = path[0] == str(url).lower()
            if path[0] == '' and url == '/':
                selected = True
            
            if selected:
                # Only return remaining path if this section is selected
                return selected, path[1:]
            else:
                return False, []
        
    ########################
    ###   URL PATTERNS
    ########################

    def patterns(self, stopAt=None):
        """Return patterns object for this section"""
        # pass self to patternList to tell it not to use patterns for any ancestor beyond it
        l = [part for part in self.patternList(stopAt)]
        return patterns('', *l)
        
    def patternList(self, stopAt=None):
        """Return list of url patterns for this section and its children"""
        if self.options.showBase or not self.children:
            # If not showing base, then there is no direct url to that section
            # But it's part of the url will be respected by the children
            for urlPattern in self.urlPattern(stopAt):
                yield urlPattern
        
        for child in self.children:
            for urlPattern in child.patternList(stopAt):
                yield urlPattern
    
    def urlPattern(self, stopAt=None):
        """Get tuple to be used for url pattern for this section"""
        for urlPattern in self.options.urlPattern(self.getPattern(stopAt), self, self.name):
            yield urlPattern

    def getPattern(self, stopAt=None):
        """Get list of patterns making the full pattern for this section"""
        if self._pattern:
            # Just return if we already have one
            return self._pattern
        
        pattern = []
        if self.parent and not self is stopAt:
            # Get parent patterns
            pattern = [p for p in self.parent.getPattern(stopAt)]
        
        match = self.options.match
        if match:
            pattern.append("(?P<%s>%s)" % (match, self.url))
        else:
            pattern.append(self.url)
        
        self._pattern = pattern
        return self._pattern
        
    def pathTo(self, section, steer, path):
        """Used to get include path to specified section"""
        inside = section == self
        return path, inside
            
########################
###
###   OPTIONS
###
########################

class Options(object):
    def __init__(self
        , admin    = False # says whether this section is showing because of admin access
        , active   = True  # says whether we should consider it at all (overrides exists and display)
        , exists   = True  # says whether the section gives a 404 when visited (overrides display)
        , display  = True  # boolean or (adminOnly, display) says whether there should be a physical link
        , showBase = True  # says whether there should be a physical link for this. Doesn't effect children
        
        # Following three are not carried over by default during a clone unless carryAll=True is given
        , alias    = None  # Says what this section will appear as in the menu
        , match    = None  # says what to match this part of the url as or if at all
        , values   = None  # Values object determining possible values for this section
        
        , kls    = None    # The view class. Can be an actual class, which will override module, or a string
        , module = None    # Determines module that view class should exist in. Can be string or actual module
        , target = None    # Name of the function to call
        
        , redirect = None  # Overrides module, kls and target
        
        , condition    = False # boolean or (adminOnly, condition) : says whether something stands in the way of this section being shown
        , needsAuth    = False # Says whether user must be authenticated to see the section
        , extraContext = None  # Extra context to put into url pattern
        , **kwargs # Catch any unexpected arguments
        ):
            
        #set everything passed in to a self.xxx attribute
        local = locals()
        args = []
        for arg in local:
            if arg not in ('self', 'kwargs'):
                args.append(arg)
                setattr(self, arg, local[arg])
        
        self._obj = None
        
        # Want to store all the values minus self for the clone method
        self.args = args[1:-1]
    
    def clone(self, **kwargs):
        """Return a copy of this object with new options.
        It Determines current options, updates with new options
        And returns a new Options object with these options
        """
        args = self.args
        if not kwargs.get('carryAll', False):
            args = [a for a in self.args if a not in ['admin', 'alias', 'match', 'values', 'showBase']]
            
        settings = dict((key, getattr(self, key)) for key in args)
        settings.update(kwargs)
        return Options(**settings)
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def show(self, request=None):
        """Determine if any dynamic conditions stand in the way of actually showing the section"""
        adminOnly = False
        condition = self.condition
        if callable(condition):
            condition = self.condition(request)
        
        if type(condition) in (tuple, list):
            adminOnly, condition = condition
        
        if adminOnly:
            self.admin = True
        
        if condition:
            return False
        
        return True
        
    def getObj(self):
        """Look at module and kls to determine either an object or string representation"""
        
        if self.kls is not None and type(self.kls) not in (str, unicode):
            # If kls is an object, we already have what we want
            obj = self.kls
        
        else:
            # Remove any dots at beginning and end of kls string
            kls = self.kls
            if self.kls is None:
                kls = ''
                
            if kls.startswith('.'):
                kls = kls[1:]
            
            if kls.endswith('.'):
                kls = kls[:-1]
               
            if  self.module is None:
                if kls == '':
                    # If module and kls are none, return None
                    return None
                else:
                    # Module is none, but kls is something, so just return kls
                    return kls
            
            if type(self.module) in (str, unicode):
                # Both module and kls are strings, just return a string
                obj = self.module
                if kls:
                    obj = '%s.%s' % (self.module, kls)
            
            else:
                obj = self.module
                if kls:
                    for next in kls.split('.'):
                        obj = getattr(obj, next)
        
        return obj
    
    def redirect_to(self, *args, **kwargs):
        if not hasattr(self, '_redirect_to'):
            from django.views.generic.simple import redirect_to
            self._redirect_to = redirect_to
        return self._redirect_to(*args, **kwargs)
    
    def urlPattern(self, pattern, section=None, name=None):
        """Return url pattern for this section"""
        if self.active:
            if pattern is None or any(p is None for p in pattern):
                pattern = '^.*'
            else:
                if type(pattern) in (tuple, list):
                    if any(part != '' for part in pattern):
                        pattern = '/'.join(pattern)
                    else:
                        pattern = ''
                    
                # Remove duplicate slashes
                pattern = regexes['multiSlash'].sub('/', pattern)
                
                if pattern == '/':
                    pattern = '^$'
                else:
                    if pattern and pattern[0] == '/':
                        pattern = pattern[1:]
                    
                    # Turn pattern into regex
                    if pattern is '':
                        pattern = '^$'
                    elif pattern.endswith('/'):
                        pattern = '^%s$' % pattern
                    else:
                        pattern = '^%s/$' % pattern
                    
            # Get redirect and call if can
            redirect = self.redirect
            if callable(self.redirect):
                redirect = self.redirect()
            
            if redirect and type(redirect) in (str, unicode):
                # Only redirect if we have a string to redirect to
                def redirector(request, url):
                    if not url.startswith('/'):
                        if request.path.endswith('/'):
                            url = '%s%s' % (request.path, url)
                        else:
                            url = '%s/%s' % (request.path, url)
                    return self.redirect_to(request, url)
                
                view = redirector
                kwargs = {'url' : unicode(redirect)}
                yield (pattern, view, kwargs, name)
        
            else:
                target = self.target
                
                if target:
                    if type(target) is FunctionType:
                        # Target is callable and not part of a class
                        # So, bypass the dispatcher
                        yield (pattern, target, self.extraContext, name)
                    elif not self.kls:
                        # There is no kls
                        # So, bypass the dispatcher
                        obj = self.getObj()
                        if obj and target:
                            obj = '%s.%s' % (obj, target)
                        elif target and not obj:
                            obj = target
                        yield (pattern, obj, self.extraContext, name)
                    else:
                        view = dispatch
                            
                        kwargs = {
                            'obj' : self.getObj(), 
                            'target' : target, 
                            'section' : section, 
                            'condition' : lambda request: not self.show(request)
                        }
                        
                        if self.extraContext:
                            kwargs.update(self.extraContext)
                            
                        yield (pattern, view, kwargs, name)
            
########################
###
###   VALUES
###
########################

class Values(object):
    def __init__(self
        , values = None   # lambda path : []
        , each   = None   # lambda path, value : (alias, urlPart)
        , asSet  = True   # says whether to remove duplicates from values
        , sorter = None   # function to be used for sorting values
        , sortWithAlias = True   # sort values by alias or the values themselves
        ):
            
        #set everything passed in to a self.xxx attribute
        local = locals()
        for arg in local:
            setattr(self, arg, local[arg])
        
        if not values:
            self.values = []
    
    def sort(self, values):
        """Determine if values can be sorted and sort appropiately"""
        # If allowed to sort
        if self.sorter:
            # Sort with a function
            # Or if not a function, just sort
            if callable(self.sorter):
                return sorted(values, self.sorter)
            else:
                return sorted(values)
        
        # Not allowed to sort, so just return as is
        return values
        
    def getValues(self, parentUrl, path, sortWithAlias=None, request=None):
        """Get transformed, sorted values"""
        # If we have values
        if self.values is not None:
            if sortWithAlias is None:
                sortWithAlias = self.sortWithAlias
            
            # Get a list of values
            if callable(self.values):
                values = list(value for value in self.values((request, parentUrl, path)))
            else:
                values = self.values
            
            # Remove duplicates
            if self.asSet:
                values = set(values)
                
            # Sort if we have to
            if not sortWithAlias:
                values = self.sort(values)
                
            # Tranform if we can
            if self.each and callable(self.each):
                ret = [self.each((request, parentUrl, path), value) for value in values]
            else:
                ret = [(value, value) for value in values]
                
            # Sort if we haven't yet
            if sortWithAlias:
                ret = self.sort(ret)
            
            return ret
        
    def getInfo(self, parentUrl, path, request=None):
        """Generator for (alias, url) pairs for each value"""
        # Get sorted values
        values = self.getValues(parentUrl, path, request=request)
            
        # Yield some information
        if values and any(v is not None for v in values):
            for alias, url in values:
                yield alias, url
        
########################
###
###   SITE
###
########################

class Site(object):
    """Object that provides include patterns for sections and sites"""
    def __init__(self, name):
        self.name = name
        
        ###   SITE INFO OBJECT
        ########################
        class Info(object):
            """Object that helps keep track of the sections and sites this site includes"""
            def __init__(self):
                self.reset()
                
            def reset(self):
                self.stuff = {}
                self.order = 1
            
            def __iter__(self):
                l = []
                for k, dicts in self.stuff.items():
                    for i, v in dicts.items():
                        l.append((v[0], (k, i) + v[1:]))
                
                # We want to maintain some order
                for _, part in sorted(l):
                    yield part
                    
            def __nonzero__(self):
                # Only nonzero if we are actually holding something
                if self.stuff:
                    return True
                else:
                    return False
            
            def __len__(self):
                return sum(len(t) for t in self.stuff.values())
            
            def add(self, obj, includeAs, patternFunc, namespace, app_name, menu=None):
                # I use a dictionary for self.stuff so I don't have the same combination of (obj, includeAs) twice
                
                if obj not in self.stuff:
                    self.stuff[obj] = {}
                    
                self.stuff[obj][includeAs] = (self.order, patternFunc, namespace, app_name, menu)
                self.order += 1
        
            def pathTo(self, section, steer, path):
                """Used to get include path to specified section"""
                inside = False
                result = []
                keys   = self.stuff.keys()
                index  = -1
                
                # I'm using a while loop so I don't iterate more than is necessary
                while index < (len(keys)-1) and not inside:
                    index     += 1
                    obj       = keys[index]
                    includes  = self.stuff[obj].keys()
                    nextSteer = []
                    
                    if not steer:
                        include = includes[0]
                    else:
                        nextSteer = steer[0]
                        if nextSteer in includes:
                            include = nextSteer
                            
                            # Steer is still current, keep using it
                            nextSteer = steer[1:]
                        else:
                            include = includes[0]
                            
                    use = [include]
                    if include is None:
                        use = []
                    
                    # Can't just compare section to obj because obj may be a site
                    # So we use pathTo on the object instead
                    result, inside = obj.pathTo(section, nextSteer, path + use)
                
                return result, inside
                
            def patterns(self):
                for obj, includeAs, patternFunc, namespace, app_name, _ in self:
                    
                    # Determine pattern
                    pattern = '^%s/'
                    if includeAs:
                        pattern = pattern % includeAs
                    else:
                        pattern = pattern % obj.url
                    
                    yield (pattern, include(patternFunc(), namespace=namespace, app_name=app_name) )
        
        ###   SITE BASE OBJECT
        ########################
        class Base(object):
            """Object for keeping track of the base of the site.
            The base is the section or site that has a urlpattern of '^'
            There should only be one of this"""
            def __init__(self):
                self.reset()
                
            def reset(self):
                self.stuff = []
                
            def __iter__(self):
                if self:
                    yield self.stuff
                    
            def __nonzero__(self):
                # Only nonzero if we actually have a base
                if self.stuff:
                    return True
                else:
                    return False
            
            def __len__(self):
                if self:
                    return 1
                else:
                    return 0
            
            def add(self, obj, includeAs, patternFunc, namespace=None, app_name=None, menu=None):
                # Just replace if there already is a base
                self.stuff = [obj, includeAs, patternFunc, namespace, app_name, menu]
        
            def pathTo(self, section, steer, path):
                """Used to get include path to specified section"""
                
                inside = False
                if self.stuff:
                    path, inside = self.stuff[0].pathTo(section, steer, path)
                
                return path, inside
                
            def patterns(self):
                for obj, includeAs, patternFunc, namespace, app_name, _ in self:
                   yield ( '^', include(patternFunc(), namespace=namespace, app_name=app_name) )

        self.info = Info()
        self.base = Base()
        
    ########################
    ###   ADD/MERGE
    ########################
    
    def getFromString(self, s):
        # Import an object using a string
        obj = s.split('.')
        module = '.'.join(obj[:-1])
        name = obj[-1]
        
        obj = __import__(module, globals(), locals(), [name], -1)
        return getattr(obj, name)
            
    def add(self, section=None, site=None, **kwargs):
        """Adds a site or section to self.info"""
        if section:
            self._addSection(section, **kwargs)
        
        elif site:
            self._addSite(site, **kwargs)
        
        else:
            raise ValueError("Must either add a section or a site")
    
    def _addSection(self, section, includeAs=None, namespace=None, app_name=None, base=False, inMenu=True):
        """Add a section to the site"""
        if type(section) in (str, unicode):
            section = self.getFromString(section)
        
        # Determine what to put in menu if anything at all
        menu = None
        if inMenu:
            menu = [section]
        
        # Determine what to add to
        add = self.info.add
        if base:
            add = self.base.add
            
        add(
            section, includeAs, lambda : section.patterns(stopAt=section), 
            namespace=namespace, app_name=app_name, menu=menu
        )
    
    def _addSite(self, site, includeAs=None, namespace=None, app_name=None, base=False, inMenu=True):
        """Add a site object to this one"""
        if type(site) in (str, unicode):
            site = self.getFromString(site)
        
        # Determine what to put in menu if anything at all
        menu = None
        if inMenu:
            # Only add sections to the menu
            menu = site.menu
            
        # Determine what to add to
        add = self.info.add
        if base:
            add = self.base.add
        
        # If we don't set includeAs, the adder will try site.url
        # Sites don't have urls. Only sections do
        if not includeAs:
            includeAs = site.name
            
        add(
            site, includeAs, site.patterns, 
            namespace=namespace, app_name=app_name, menu=menu
        )
    
    def merge(self, site, keepBase=False):
        """Merge another site with this one"""
        for section in site.info:
            self.info.add(*section)
        
        if not keepBase:
            # Only add base from new site if we don't want to keep current base
            for section in site.base:
                self.base.add(*section)
            
    ########################
    ###   MAKING A BASE
    ########################
    
    def makeBase(self, inMenu=False):
        """Make and return a section representing the base of the site"""
        base = Section('', name=self.name).base(showBase=False)
        self.add(base, base=True, inMenu=inMenu, namespace=self.name, app_name=self.name)
        
        return base
            
    ########################
    ###   URL PATTERNS
    ########################
    
    def includes(self):
        """All the (pattern, include) tuples for this site"""
        for pat in self.base.patterns():
            yield pat
        
        for pat in self.info.patterns():
            yield pat
    
    def patterns(self, stopAt=None):
        """Wraps self.includes in a patterns object"""
        # The stopAt argument isn't used, 
        # but is there to mimic the patterns method of the Sections object
        l = [l for l in self.includes()]
        return patterns('', *l)
            
    ########################
    ###   MENU/SECTIONS
    ########################
    
    def menu(self):
        """Return a list of sections that form the menu"""
        collected = []
        for collection in [self.base, self.info]:
            for _, _, _, _, _, menu in collection:
                if menu:
                    if callable(menu):
                        menu = menu()
                    for m in menu:
                        if m not in collected:
                            collected.append(m)
        
        return collected

    def getPath(self, section, path):
        """Return (parentUrl, remainingUrl, isInside) tuple given desired section and actual path"""
        
        parentUrl, inside = self.pathTo(section, steer=path[:])
        if not inside:
            # Section doesn't even belong to the site !
            return [], path, False
        
        for item in parentUrl:
            if path : path.pop(0)
        
        return parentUrl, path, inside

    def pathTo(self, section, steer=None, path=None):
        """Determines url to get to specified section.
        When a section is added to a site, there is no reference to the site on the section.
        This is because we may add the section to many sites.
        Also, when adding to the site we specified what to include the section as, which again isn't on the section.
        
        Hence the only way to get this information is to ask the site how to get to this section.
        
        Arguments :
            section = Section we're attempting to find
            steer = Sections can be included under many names. Steer steers to specific includes 
                    (will quietly ignore if it's rubbish)
            path = Path collected so far (pathTo may be called on other sites in the process)
            
            Path and steer must both be lists, not strings (so url.split('/'))
        """
        
        if not path:
            path = []
            
        if not steer:
            steer = []
        
        # If we have steer, then perhaps we should look inside stuff first
        # Otherwise if it's in base as well it will override every time
        first = self.base.pathTo
        second = self.info.pathTo
        if steer:
            first, second = second, first
        
        result, inside = first(section, steer, path)
        if not inside:
            result, inside = second(section, steer, path)
        
        return result, inside
            
    ########################
    ###   OTHER
    ########################
    
    def reset(self):
        self.base.reset()
        self.info.reset()
        
    def __repr__(self):
        return '<CWF SITE : %s>' % self.name
