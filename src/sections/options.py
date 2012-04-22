from errors import ConfigurationError
from dispatch import dispatcher
import inspect
import re

########################
###   EXTRAS
########################

regexes = {
      'multiSlash' : re.compile('/+')
    , 'valid_import' : re.compile('^[\w_]+[0-9a-zA-Z_]*$')
    }

class Empty(object): pass

########################
###   OPTIONS
########################
    
class Options(object):
    def __init__(self):
        # Some flags to determine what to show
        # These may be callables that accept (request)
        # admin: Flag to hardcode that this is only visible due to admin privelege
        # active: Overrides exists and display to disable viewing and visiting
        # exists: Overrides display to disable viewing and visiting
        # display: Says whether this should be displayed
        #     active, exists and display affect children as well
        self.admin = False
        self.active = True
        self.exists = True
        self.display = True
        
        # Some settings for determining view
        # kls: The view class. Can be the kls itself or a string name of the kls
        # module: Where to find the kls if the kls is specified as a string. (can be object or location)
        # target: The function on the kls to invoke
        # redirect will override kls, module and target
        # extra_content: Extra request context to give the view
        self.kls = None
        self.module = None
        self.target = None
        self.redirect = None
        self.extra_content = None
        
        # Determine what to show in the menu
        # alias: what appears in the menu
        # match: Determine if this part of the url should be given to the view as a keyword argument
        #   The value given will be the name this part of the url is given as
        # values: Values object determining possible values as child elements in the menu
        # needs_auth: Either string, list of strings or boolean
        #   If boolean: Says whether request.user.is_authenticated() must be true for display and visiting
        #   If string or list of strings: The permissions request.user must have for display and visiting
        # promote_children: Says whether children should be displayed at this level instead of displaying this
        self.alias = None
        self.match = None
        self.values = None
        self.needs_auth = False
        self.promote_children = True

    ########################
    ###   SETTERS
    ########################
        
    def setters(self):
        '''Determine each setter method and required args for that method'''
        for method in ('set_conditionals', 'set_view', 'set_menu'):
            func = getattr(self, method)
            required = dict(arg for arg in inspect.getargspec(func).args if arg != 'self')
            yield func, required
    
    def set_everything(self, **kwargs):
        '''
            Call the setters using one method
            Will make sure everything in kwargs is passed into the setters
            And that the setters don't duplicate settings
        '''
        taken = []
        for method, required in self.setters():            
            values = {}
            for arg in required:
                if arg in taken:
                    raise ConfigurationError("%s takes argument (%s) already taken elsewhere..." % (method, arg))
                    taken.append(arg)
                if arg in kwargs:
                    values[arg] = kwargs[arg]
            func(**values)
        
        leftover = set(kwargs.keys()) - set(taken)
        if leftover:
            raise ConfigurationError("Arguments provided into set_everything that wasn't consumed (%s)" % leftover)
    
    def set_conditionals(self, admin=Empty, active=Empty, exists=Empty, display=Empty):
        '''
            Set conditionals
            These are either booleans or callable objects that take in one argument
            ConfigurationError will be raised if this is not the case
        '''
        vals = (('admin', admin), ('active', active), ('exists', exists), ('display', display), ('show_base', show_base))
        for name, val in vals:
            if val is not Empty:
                if type(val) is not bool and not callable(val):
                    raise ConfigurationError(
                        "Conditionals must be boolean or callable(request). Not %s (%s=%s)" % (type(val), name, val)
                        )
                
                if callable(val):
                    if hasattr(val, 'im_func'):
                        needed = 2
                    else:
                        needed = 1
                    
                    args = inspect.getargspec(val).args
                    num_args = len(args)
                    if num_args != needed:
                        raise ConfigurationError(
                            "Conditionals as callables must only accept one argument, not %s (%s)" % (num_args, args)
                            )
                    
                setattr(self, name, val)
    
    def set_view(self, kls=Empty, module=Empty, target=Empty, redirect=Empty, extra_content=Empty):
        '''Set options for specifying the view'''
        vals = (
              ('kls', kls), ('module', module), ('target', target)
            , ('redirect', redirect), ('extra_content', extra_content)
            )
        for name, val in vals:
            if val is not Empty:
                if type(val) not in (str, unicode) and val is not callable(val):
                    raise ConfigurationError(
                        "%s must be either a string or a callble, not %s (%s)" % (
                            name, type(self.redirect), self.redirect
                        )
                    )
                setattr(self, name, val)
    
    def set_menu(self, alias=Empty, match=Empty, values=Empty, needs_auth=Empty, promote_children=Empty):
        '''Set options for what appears in the menu'''
        vals = (('alias', alias), ('match', match), ('values', values), ('needs_auth', needs_auth))
        for name, val in vals:
            if val is not Empty:
                setattr(self, name, val)
        
        if not hasattr(values, 'getInfo'):
            raise ConfigurationError(
                "Values must have a get_info method to get information from. %s does not" % self.values
                )

    ########################
    ###   CLONE
    ########################
    
    def clone(self, **kwargs):
        """
            Return a copy of this object with new options.
            It Determines current options, updates with new options
            And returns a new Options object with these options
        """
        passon = []
        for _, required in self.setters():
            passon.extend(required)
        
        no_propogate = ('admin', 'alias', 'match', 'values', 'show_base')
        values = dict((name, kwargs[arg]) for arg in passon if arg not in no_propogate and arg in kwargs)
        
        cloned = Options()
        cloned.set_everything(**values)
        return cloned

    ########################
    ###   URL PATTERN
    ########################
    
    def create_pattern(self, url_parts):
        '''Determine pattern for this url'''
        if type(pattern) in (str, unicode):
            pattern = [pattern]
        
        # Pattern was nothing, make anything url
        if len(pattern) is 1 and pattern[0] is None:
            return '^.*'
        
        # Turn pattern back into a single string
        if len(pattern) is 1 and pattern[0] == '':
            pattern = ''
        else:
            pattern = '/'.join(pattern)
            
        # Remove duplicate slashes
        pattern = regexes['multiSlash'].sub('/', pattern)
        
        # Pattern was empty string or multiple slashes, make empty url
        if pattern in ('/', ''):
            return '^$'
        
        # Removing leading slash
        # Already deduplicated slashes
        if pattern[0] == '/':
            pattern = pattern[1:]
        
        # Turn pattern into regex
        if pattern.endswith('/'):
            pattern = '^%s$' % pattern
        else:
            pattern = '^%s/$' % pattern

    ########################
    ###   URL VIEW
    ########################
    
    def url_view(self, section):
        """Return url view for these options"""
        if self.redirect:
            # Redirect overrides other options
            return self.redirect_view(self.redirect, section)
        
        target = self.target
        if type(target) not in (str, unicode):
            # Target already a callabel
            return target, self.extra_context
        
        kls = self.get_view_kls()
        view = dispatcher
        kwargs = dict(kls=kls, target=target, section=section)
        return view, kwargs

    def redirect_view(self, redirect, section):
        '''Return function to be used for redirection'''
        def redirector(request, redirect=redirect):
            url = redirect
            if callable(redirect):
                url = redirect(request)
            
            if not url:
                raise Http404
            
            if not url.startswith('/'):
                if request.path.endswith('/'):
                    url = '%s%s' % (request.path, url)
                else:
                    url = '%s/%s' % (request.path, url)
            return self.redirect_to(request, url)
        return redirector, self.extra_context
        
    def get_view_kls(self):
        '''Determine view kls by looking at module and kls'''
        if not self.kls and not self.module:
            # No view to be determined
            return None
        
        if self.kls is not None and type(self.kls) not in (str, unicode):
            # kls is already an object
            return self.kls
        
        kls = self.clean_module_name(self.kls)
        if not module:
            # No module, return kls as a string
            return kls
        
        if type(self.module) not in (str, unicode):
            # Module is a string, concatenate with kls
            module = self.clean_module_name(self.module)
            return "%s.%s" % (self.module, self.kls)
        
        else:
            # Module is an object
            # getattr each part of kls from it
            result = module
            for next in kls.split('.'):
                result = getattr(result, next)
            return result

    ########################
    ###   HELPERS
    ########################
    
    def reachable(self, request):
        """Determine if options say this exists and has permissions for this request"""
        if not self.conditional('exists', request) or not self.conditional('active', request):
            # Not active or doesn't exist
            return False
        return self.has_permissions(request.user)

    ########################
    ###   UTILITY
    ########################
    
    def conditional(self, name, request):
        '''Return conditional. If conditional is callable, return result of calling with request'''
        val = getattr(self, name)
        if callable(val):
            return val(request)
        else:
            return val
    
    def hasPermissions(self, user):
        '''Determine if user has permissions given these options'''
        needsAuth = self.needsAuth
        if not needsAuth:
            return True
        
        if type(needsAuth) is bool:
            return user.is_authenticated()
        else:
            def iterAuth():
                if type(needsAuth) in (list, tuple):
                    for auth in needsAuth:
                        yield auth
                else:
                    yield needsAuth
            
            return all(user.has_perm(auth) for auth in iterAuth())
    
    def clean_module_name(self, kls):
        '''
            * Remove dots from beginning and end of kls string
            * Complain about spaces and non-ascii characters
        '''
        while kls.startswith('.'):
            kls = kls[1:]
        
        while kls.endswith('.'):
            kls = kls[:-1]
        
        if ' ' in kls:
            raise ConfigurationError("%s is not a valid import location" % kls)
        
        for part in kls.split('.'):
            if not regexes['valid_import'].match(kls):
                raise ConfigurationError("%s is not a valid import location" % kls)
        
        return kls
