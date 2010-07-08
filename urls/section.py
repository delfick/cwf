from django.conf.urls.defaults import include, patterns
from django.views.generic.simple import redirect_to
from django.http import Http404
from itertools import chain
from dispatch import dispatch

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
        self.options  = None
        self.children = []
        
        self._pattern  = None
        
        if hasattr(self, 'setup'):
            self.setup()
    
    def add(self, url, match, name=None):
        """Adds a child to self.children"""
        if url == '':
            raise ValueError("Use section.first() to add a section with same url as parent")
        
        section = Section(url=url, name=name, parent=self)
        section.giveOptions(self.options.clone(match=match))
        self.children.append(section)
        
        return section

    def first(self, match, name=None):
        """Adds a child with the same url as the parent at the beginning of self.children"""
        section = Section(url="", name=name, parent=self)
        section.giveOptions(self.options.clone(match=match))
        self.children.insert(0, section)
        
        return section
        
    def base(self, **kwargs):
        """Extends self.options with the given keywords"""
        self.options = Options(**kwargs)
        return self
        
    ########################
    ###   SPECIAL
    ########################
    
    def __getattr__(self, key):
        if key == 'options':
            if not object.__getattribute__(self, key):
                return Options()
        
        return super(Section, self).__getattr__(key)
    
    def __iter__(self):
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
        if self.parent:
            return self.parent.rootAncestor()
        else:
            return self
        
    def show(self):
        parentShow = True
        if self.parent:
            parentShow = self.parent.show()
        
        if parentShow:
            return self.options.show()
        
        return False
        
    def appear(self):
        return self.options.display and self.show()
    
    def getInfo(self, path, parentUrl=None, gen=None):
        if self.options.active and self.options.exists and self.appear():
            def get(path, url=None):
                """Helper to get children, fullUrl and determine if selected"""
                if not url:
                    url = self.url
                    
                path, selected = determineSelection(path, url)
                
                
                if not parentUrl:
                    fullUrl = []
                else:
                    fullUrl = parentUrl[:]
                    
                if url:
                    fullUrl.append(url)
                    
                children = self.children
                if gen:
                    # Make it a lambda, so that template can remake the generator
                    # Generator determines how to deliver info about the children
                    children = lambda : gen(self.children, fullUrl, path)()
                    
                return selected, children, fullUrl
                
            if self.options.values:
                for alias, url in self.values.getInfo(path, gen):
                    selected, children, fullUrl = get(path, url)
                    yield (url, fullUrl, alias, selected, children, self.options)
            else:
                selected, children, fullUrl = get(path)
                yield (self.url, fullUrl, self.options.alias, selected, children, self.options)
    
    def determineSelection(path, url=None):
        if not url:
            url = self.url
            
        if self.showBase:
            selected = path[0] == url
            return path[1:], selected
        
        elif self.parent:
            path, parentSelected = self.parent.determineSelection(path)
            selected = parentSelected and path[0] == url
            return selected, path[1:]
        
        return False, path
        
    ########################
    ###   URL PATTERNS
    ########################

    def patterns(self):
        l = [part for part in self.patternList()]
        return patterns('', *l)
        
    def patternList(self):
        if section.showBase or not self.children:
            # If not showing base, then there is no direct url to that section
            # But it's part of the url will be respected by the children
            for urlPattern in self.urlPattern():
                yield urlPattern
        
        for child in self.children:
            for urlPattern in child.getPatternList():
                yield urlPattern
    
    def urlPattern(self):
        for urlPattern in self.options.urlPattern(self.getPattern(), self, self.name):
            yield urlPattern

    def getPattern(self):
        if self._pattern:
            return self._pattern
        
        pattern = []
        if self.parent:
            pattern = [p for p in self.parent.getPattern()]
        
        match = self.options.match
        if match:
            pattern.append("(?P<%s>%s)" % (match, self.url))
        else:
            pattern.append(self.url)
        
        self.pattern = pattern
        return self.pattern
            
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
        
        , alias    = None  # Says what this section will appear as in the menu
        , match    = None  # says what to match this part of the url as or if at all
        , values   = None  # Values object determining possible values for this section
        
        , kls    = "Views" # The view class. Can be an actual class, which will override module, or a string
        , module = None    # Determines module that view class should exist in. Can be string or actual module
        , target = 'base'  # Name of the function to call
        
        , redirect = None  # Overrides module, kls and target
        
        , condition    = False # says whether something stands in the way of this section being shown
        , extraContext = None  # Extra context to put into url pattern
        ):
            
        #set everything passed in to a self.xxx attribute
        import inspect
        args, _, _, _ = inspect.getargvalues(inspect.currentframe())
        for arg in args:
            setattr(self, arg, locals()[arg])
            
        if not self.alias:
            self.alias = self.name.capitalize()
        
        self._obj = None
        
        # Want to store all the values minus self for the clone method
        self.args = args[1:]
    
        
    def clone(self, **kwargs):
        """Return a copy of this object with new options.
        It Determines current options, updates with new options
        And returns a new Options object with these options
        """
        settings = dict(key == getattr(self, key) for key in self.args)
        settings.update(kwargs)
        return Options(**settings)

    def show(self):
        """Determine if any dynamic conditions stand in the way of actually showing the section"""
        condition = self.condition
        if callable(condition):
            condition = condition()
        
        if condition:
            return True
        
        return False
        
    def getObj(self):
        """Look at module and kls to determine either an object or string representation"""
        
        if type(self.kls) not in (str, unicode):
            # If kls is an object, we already have what we want
            obj = self.kls
        
        else:
            # Remove any dots at begninning and end of kls string
            kls = self.kls
            if kls.startswith('.'):
                kls = kls[1:]
            
            if kls.endswith('.'):
                kls = kls[:-1]
                
            if  type(self.module) in (str, unicode):
                # Both module and kls are strings, just return a string
                obj = '%s.%s' % (self.module, self.kls)
            
            else:
                if '.' not in self.kls:
                    # Kls is just an attribute of the module
                    obj = getattr(self.module, self.kls)
                else:
                    # Kls is more than just an attribute, so return a string
                    obj = '%s.%s' % (self.module.__name__, self.kls)
        
        return obj
    
    def urlPattern(self, pattern, section, name=None):
        """Return url pattern for this section"""
        if self.active and self.exists:
            if type(pattern) in (tuple, list):
                pattern = '/'.join(pattern)
                
            # Remove duplicate slashes
            pattern = pattern.replace('//', '/')
            
            # Turn pattern into regex
            pattern = '^%s/?$' % pattern
            
            if self.redirect:
                view = redirect_to
                kwargs = {'url' : str(self.redirect)}
                yield (pattern, view, kwargs, name)
        
            else:
                view = dispatch
                
                target = self.target
                if callable(target):
                    target = target()
                    
                kwargs = {'obj' : self.getObj(), 'target' : target, 'section' : section, 'condition' : self.show}
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
    def __init__(self, name):
        self.name = name
        self._base = None
        
        self.menu = []
        self.merged = []
        self.sections = []
        self.patterns = []
    
    def merge(site, includeAs=None, namespace=None, app_name=None, base=False, inMenu=False):
        if type(site) in (str, unicode):
            site = __import__('.'.join(site[:-1]), globals(), locals(), [site[-1]], -1)
            
        self.merged.eppend(site)
        if inMenu:
            self.menu.extend(site.menu)
        self.sections.extend(site.sections)
        
        pattern = '^%s$'
        if base:
            pattern = pattern % ''
        else:
            if includeAs:
                pattern = pattern % includeAs
            else:
                pattern = pattern % site.name
                
        self.patterns.append((pattern, include(site.urls(), namespace=namespace, app_name=app_name)))
    
    def add(section, includeAs=None, namespace=None, app_name=None, base=False, inMenu=False):
        if type(section) in (str, unicode):
            section = __import__('.'.join(section[:-1]), globals(), locals(), [section[-1]], -1)
        
        self.sections.append(section)
        if inMenu:
            self.menu.append(section)
        
        pattern = '^%s/?$'
        if base:
            pattern = pattern % ''
        else:
            if includeAs:
                pattern = pattern % includeAs
            else:
                pattern = pattern % section.url
        
        l = [part for pat in section.patternList()]
        self.patterns.append((pattern, include(l, namespace=namespace, app_name=app_name)))
    
    def makeBase(self):
        if self._base:
            return self._base
        
        self._base = Section('', site.name)
        self.patterns.append(
            lambda : (pattern, include([part for pat in self._base.patternList()], app_name=self.name, namespace=self.name))
        )
        
        return self._base
        
    def urls(self):
        l = []
        for pattern in self.patterns:
            if callable(pattern):
                l.append(pattern())
            else:
                l.append(pattern)
                
        return patterns('', *l)
        
########################
###
###   MENU
###
########################

class Menu(object):
    def __init__(self, site, selectedSection, remainingUrl):
        self.site = site
        self.remainingUrl = remainingUrl
        self.selectedSection = selectedSection
    
    def getGlobal(self):
        for section in self.site:
            if section == self.selectedSection:
                section.selected = True
            else:
                section.selected = False
            yield section.getInfo(self.remainingUrl)
        
    def heirarchial(self, section=None, path=None, parentUrl=None):
        if not section:
            section = self.selectedSection
            
        if not path:
            path = [p for p in self.remainingUrl]
        
        if parentUrl is None:
            parentUrl = []
            
        if section.options.showBase:
            for info in section.getInfo(path, parentUrl, self.heirarchial):
                yield info
            
        else:
            if section.url:
                parentUrl.append(section.url)
                
            for child in section.children:
                yield child.getInfo(path, parentUrl, self.hierarchial)
                
    def layered(self, selected=None, path=None, parentUrl = None):
        if not selected:
            selected = self.selectedSection
        
        if not path:
            path = [p for p in self.remainingUrl]
            
        if parentUrl is None:
            parentUrl = []
            
        while selected:
            l = []
            anySelected = False
            for part in self.getLayer(selected, path, parentUrl):
                l.append(part)
                _, _, _, isSelected, _, _ = part
                if isSelected:
                    selected = part
                    anySelected = True
            
            if not anySelected:
                selected = None
        
        yield l
    
    def getLayer(self, section, path, parentUrl):
        if section.options.showBase:
            yield section.getInfo(path, parenturl, self.layered)
        
        else:
            if section.url:
                parentUrl.append(section.url)
                
            l = [child.getLayer(child, path) for child in section.children]
            for part in chain.from_iterable(l):
                yield part.getInfo(path, parentUrl, self.layered)
    
