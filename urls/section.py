from django.conf.urls.defaults import include, patterns
from django.views.generic.simple import redirect_to
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

    def first(self, match=None, name=None):
        """Adds a child with the same url as the parent at the beginning of self.children"""
        if self.children and self.children[0].url == '':
            # Override if we already have a first section
            self.children.pop(0)
        
        section = Section(url="", name=name, parent=self)
        section.options = self.options.clone(match=match)
        self.children.insert(0, section)
        
        return section
        
    def base(self, **kwargs):
        """Extends self.options with the given keywords"""
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
    
    def __getattr__(self, key):
        if key == 'options':
            # Always want to have an options object
            # To avoid creating one unecessarily, we lazily create it
            current = object.__getattribute__(self, '_options')
            if not current:
                opts = Options()
                self._options = opts
                return opts
            else:
                return current
        
        return object.__getattribute__(self, key)
    
    def __setattr__(self, key, value):
        if key == 'options':
            # So I don't need a try..except in __getattr__, I put options under self._options
            # This is so I can have self._options = None in __init__
            # If I have self.options = None in __init__, __getattr__ is never called for self.options
            self._options = value
        
        else:
            super(Section, self).__setattr__(key, value)
            
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
        
    def show(self):
        """Can only show if options say this section can show and parent can show"""
        parentShow = True
        if self.parent:
            parentShow = self.parent.show()
        
        if parentShow:
            return self.options.show()
        
        return False
        
    def appear(self):
        """Can only appear if allowed to be displayed and shown"""
        return self.options.display and self.show()
    
    def getInfo(self, path, parentUrl=None, parentSelected=True, gen=None):
        if self.options.active and self.options.exists and self.show():
            def get(path, url=None):
                """Helper to get children, fullUrl and determine if selected"""
                if not url:
                    url = self.url
                
                if url.startswith('/'):
                    url = url[1:]
                    
                selected, path = self.determineSelection(path, parentSelected, url)
                
                if not parentUrl:
                    fullUrl = []
                else:
                    fullUrl = parentUrl[:]
                    
                if url is not None:
                    fullUrl.append(url)
                
                children = self.children
                if self.children:
                    if gen:
                        # Make it a lambda, so that template can remake the generator
                        # Generator determines how to deliver info about the children
                        children = lambda : gen(self.children, path, fullUrl, selected)
                
                # We want absolute paths
                if fullUrl and fullUrl[0] != '':
                    fullUrl.insert(0, '')
                    
                return selected, children, fullUrl
                
            if self.options.values:
                for alias, url in self.options.values.getInfo(path):
                    selected, children, fullUrl = get(path, url)
                    yield (self, fullUrl, alias, selected, children, self.options)
            else:
                alias = self.options.alias
                if not alias:
                    alias = self.url.capitalize()
                selected, children, fullUrl = get(path)
                yield (self, fullUrl, alias, selected, children, self.options)
    
    def determineSelection(self, path, parentSelected, url=None):
        """Return True and rest of path if selected else False and no path."""
        if not parentSelected or not path:
            return False, []
        else:
            if not url:
                url = self.url
            
            # Already checked that path is not empty
            selected = path[0] == url
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

    def patterns(self):
        """Return patterns object for this section"""
        # pass self to patternList to tell it not to use patterns for any ancestor beyond it
        l = [part for part in self.patternList(self)]
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
            
########################
###
###   OPTIONS
###
########################

class Options(object):
    def __init__(self
        , active   = True  # says whether we should consider it at all (overrides exists and display)
        , exists   = True  # says whether the section gives a 404 when visited (overrides display)
        , display  = True  # says whether there should be a physical link
        , showBase = True  # says whether there should be a physical link for this. Doesn't effect children
        
        # Following three are not carried over by default during a clone unless carryAll=True is given
        , alias    = None  # Says what this section will appear as in the menu
        , match    = None  # says what to match this part of the url as or if at all
        , values   = None  # Values object determining possible values for this section
        
        , kls    = "Views" # The view class. Can be an actual class, which will override module, or a string
        , module = None    # Determines module that view class should exist in. Can be string or actual module
        , target = 'base'  # Name of the function to call
        
        , redirect = None  # Overrides module, kls and target
        
        , condition    = False # says whether something stands in the way of this section being shown
        , needsAuth    = False # Says whether user must be authenticated to see the section
        , extraContext = None  # Extra context to put into url pattern
        , **kwargs # Catch any unexpected arguments
        ):
            
        #set everything passed in to a self.xxx attribute
        import inspect
        args, _, _, _ = inspect.getargvalues(inspect.currentframe())
        for arg in args:
            if arg != 'kwargs':
                setattr(self, arg, locals()[arg])
        
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
            args = [a for a in self.args if a not in ['alias', 'match', 'values']]
            
        settings = dict((key, getattr(self, key)) for key in args)
        settings.update(kwargs)
        return Options(**settings)
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def show(self):
        """Determine if any dynamic conditions stand in the way of actually showing the section"""
        condition = self.condition
        if callable(condition):
            condition = condition()
        
        if condition:
            return False
        
        return True
        
    def getObj(self):
        """Look at module and kls to determine either an object or string representation"""
        
        if self.kls is not None and type(self.kls) not in (str, unicode):
            # If kls is an object, we already have what we want
            obj = self.kls
        
        else:
            # Remove any dots at begninning and end of kls string
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
                obj = '%s.%s' % (self.module, self.kls)
            
            else:
                obj = self.module
                for next in kls.split('.'):
                    obj = getattr(obj, next)
        
        return obj
    
    def urlPattern(self, pattern, section=None, name=None):
        """Return url pattern for this section"""
        if self.active and self.exists:
            if type(pattern) in (tuple, list):
                pattern = '/'.join(pattern)
                
            # Remove duplicate slashes
            pattern = regexes['multiSlash'].sub('/', pattern)
            
            # Turn pattern into regex
            if pattern.endswith('/'):
                pattern = '^%s$' % pattern
            else:
                pattern = '^%s/?$' % pattern
            
            # Get redirect and call if can
            redirect = self.redirect
            if callable(self.redirect):
                redirect = self.redirect()
            
            if redirect and type(redirect) in (str, unicode):
                # Only redirect if we have a string to redirect to
                view = redirect_to                    
                kwargs = {'url' : unicode(redirect)}
                yield (pattern, view, kwargs, name)
        
            else:
                target = self.target
                
                if type(target) is FunctionType:
                    # Target is callable and not part of a class
                    # So bypass the dispatcher
                    yield (pattern, target, self.extraContext, name)
                else:
                    view = dispatch
                        
                    kwargs = {
                        'obj' : self.getObj(), 'target' : target, 'section' : section, 'condition' : self.show
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
        , asSet  = False  # says whether to remove duplicates from values
        , sorter = None   # function to be used for sorting values
        , sortWithAlias = True   # sort values by alias or the values themselves
        ):
            
        #set everything passed in to a self.xxx attribute
        import inspect
        args, _, _, _ = inspect.getargvalues(inspect.currentframe())
        for arg in args:
            setattr(self, arg, locals()[arg])
        
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
        
    def getValues(self, path, sortWithAlias=None):
        """Get transformed, sorted values"""
        # If we have values
        if self.values is not None:
            if sortWithAlias is None:
                sortWithAlias = self.sortWithAlias
            
            # Get a list of values
            if callable(self.values):
                values = list(value for value in self.values(path))
            else:
                values = self.values
            
            # Sort if we have to
            if not sortWithAlias:
                values = self.sort(values)
                
            # Tranform if we can
            if self.each and callable(self.each):
                ret = [self.each(path, value) for value in values]
            else:
                ret = [(value, value) for value in values]
                
            # Sort if we haven't yet
            if sortWithAlias:
                ret = self.sort(ret)
                
            # Remove duplicates
            if self.asSet:
                ret = set(ret)
                
            return ret
        
    def getInfo(self, path):
        """Generator for (alias, url) pairs for each value"""
        # Get sorted values
        values = self.getValues(path)
            
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
                self.stuff = {}
                self.order = 1
            
            def __iter__(self):
                l = []
                for k, v in self.stuff.items():
                    l.append((v[0], k + v[1:]))
                
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
                return len(self.stuff)
            
            def add(self, obj, includeAs, patternFunc, namespace, app_name, menu=None):
                # I use a dictionary for self.stuff so I don't have the same combination of (obj, includeAs) twice
                self.stuff[(obj, includeAs)] = (self.order, patternFunc, namespace, app_name, menu)
                self.order += 1
                
            def patterns(self):
                for obj, includeAs, patternFunc, namespace, app_name, _ in self:
                    
                    # Determine pattern
                    pattern = '^%s/?$'
                    if includeAs:
                        pattern = pattern % includeAs
                    else:
                        pattern = pattern % obj.url
                    
                    yield (pattern, include(patternFunc, namespace=namespace, app_name=app_name) )
        
        ###   SITE BASE OBJECT
        ########################
        class Base(object):
            """Object for keeping track of the base of the site.
            The base is the section or site that has a urlpattern of '^$'
            There should only be one of this"""
            def __init__(self):
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
                #set everything passed in to a self.xxx attribute
                import inspect
                args, _, _, _ = inspect.getargvalues(inspect.currentframe())
                
                # Just replace if there already is a base
                self.stuff = [locals()[a] for a in args[1:]]
                
            def patterns(self):
                for obj, includeAs, patternFunc, namespace, app_name, _ in self:
                   yield ( '^$', include(patternFunc, namespace=namespace, app_name=app_name) )

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
    
    def _addSection(self, section, includeAs=None, namespace=None, app_name=None, base=False, inMenu=False):
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
    
    def _addSite(self, site, includeAs=None, namespace=None, app_name=None, base=False, inMenu=False):
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
        base = Section('', name=self.name)
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
    
    def patterns(self):
        """Wraps self.includes in a patterns object"""
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
