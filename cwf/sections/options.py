from errors import ConfigurationError
from dispatch import dispatcher

import inspect
import re

########################
###   EXTRAS
########################

regexes = {
      'multiSlash' : re.compile('/+')
    , 'valid_import' : re.compile('^[a-zA-Z_]+[0-9a-zA-Z_]*$')
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
        # extra_context: Extra request context to give the view
        self.kls = None
        self.module = None
        self.target = None
        self.redirect = None
        self.extra_context = None

        # Some options for having a section as a django include
        self.app_name = None
        self.namespace = None

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
        self.promote_children = False
        self.propogate_display = True

    ########################
    ###   SETTERS
    ########################

    def setters(self):
        '''Determine each setter method and required args for that method'''
        for method in ('set_conditionals', 'set_view', 'set_urlname', 'set_menu'):
            func = getattr(self, method)
            required = list(arg for arg in inspect.getargspec(func).args if arg != 'self')
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

                if arg in kwargs:
                    taken.append(arg)
                    values[arg] = kwargs[arg]
            method(**values)

        leftover = set(kwargs.keys()) - set(taken)
        if leftover:
            leftover = ', '.join("'%s'" % name for name in sorted(leftover))
            raise ConfigurationError("Arguments provided into set_everything that wasn't consumed (%s)" % leftover)

    def set_conditionals(self, admin=Empty, active=Empty, exists=Empty, display=Empty):
        '''
            Set conditionals
            These are either booleans or callable objects that take in one argument
            ConfigurationError will be raised if this is not the case
        '''
        vals = (('admin', admin), ('active', active), ('exists', exists), ('display', display))

        for name, val in vals:
            if val is not Empty:
                if type(val) is not bool and not callable(val):
                    raise ConfigurationError(
                        "Conditionals must be boolean or callable(request), not %s (%s=%s)" % (type(val), name, val)
                        )

                if callable(val):
                    if hasattr(val, 'im_func'):
                        needed = 2
                    else:
                        needed = 1

                    check = val
                    if not inspect.isfunction(check) and not inspect.ismethod(check):
                        check = getattr(val, '__call__')

                    args = inspect.getargspec(check).args
                    num_args = len(args)
                    if num_args != needed:
                        raise ConfigurationError(
                            "Conditionals as callables must only accept one argument, not %s (%s)" % (num_args, args)
                            )

                setattr(self, name, val)

    def set_view(self, kls=Empty, module=Empty, target=Empty, redirect=Empty, extra_context=Empty):
        '''Set options for specifying the view'''
        vals = (
              ('kls', kls), ('module', module), ('target', target)
            , ('redirect', redirect), ('extra_context', extra_context)
            )
        for name, val in vals:
            if val is not Empty:
                valid_extra_context = name == 'extra_context' and type(val) is dict
                if name != 'extra_context' or not valid_extra_context:
                    if val is not None and type(val) not in (str, unicode) and not callable(val):
                        raise ConfigurationError(
                            "%s must be either a string or a callble, not %s (%s)" % (
                                name, type(val), val
                            )
                        )
                setattr(self, name, val)

    def set_menu(self
        , alias=Empty, match=Empty, values=Empty, needs_auth=Empty
        , propogate_display=Empty, promote_children=Empty
        ):
        '''Set options for what appears in the menu'''
        vals = (
              ('alias', alias), ('match', match), ('values', values), ('needs_auth', needs_auth)
            , ('propogate_display', propogate_display), ('promote_children', promote_children)
            )

        for name, val in vals:
            if val is not Empty:
                setattr(self, name, val)

        if values is not Empty and values is not None and (not hasattr(values, 'get_info') or not callable(values.get_info)):
            raise ConfigurationError(
                "Values must have a get_info method to get information from. %s does not" % self.values
                )

    def set_urlname(self, namespace=Empty, app_name=Empty):
        """Set options for what's put in a django include if that is used to create patterns for this section"""
        vals = (('namespace', namespace), ('app_name', app_name))
        for name, val in vals:
            if val is not Empty:
                setattr(self, name, val)

    ########################
    ###   URL PATTERN
    ########################

    def create_pattern(self, url_parts):
        '''
            Determine pattern for this url
            If no url parts, use '.*'

            if pattern is empty or just a slash then use '^$'
            otherwise
              * Prepend with ^
              * And end with /$ if doesn't already end with a slash
        '''
        pattern = self.string_from_url_parts(url_parts)
        if pattern is None:
            # No url_parts, give anything pattern
            pattern = '.*'

        # Removing leading slash
        # Already deduplicated slashes
        if pattern and pattern[0] == '/':
            pattern = pattern[1:]

        if pattern == '':
            pattern = '^$'
        else:
            pattern = "^%s" % pattern

            if pattern[-1] != '/':
                pattern = "%s/$" % pattern

        return pattern

    def string_from_url_parts(self, url_parts):
        """
            Get a string from url_parts that is joined by slashes and has no multiple slashes
            If url_parts itself is None, then None will be returned
        """
        if type(url_parts) not in (list, tuple):
            url_parts = [url_parts]

        # Pattern was nothing, make anything url
        if len(url_parts) is 1 and url_parts[0] is None:
            return None
        else:
            # Turn url_parts back into a single string
            if len(url_parts) is 1 and url_parts[0] == '':
                pattern = ''
            else:
                pattern = '/'.join(url_parts)

            # Remove duplicate slashes
            return regexes['multiSlash'].sub('/', pattern)

    ########################
    ###   URL VIEW
    ########################

    def url_view(self, section):
        """
            Return url view for these options
            If redirect is specified, return redirect view
            If target is already callable, return target along with extra_context

            Otherwise, determine view kls
            and return dispatcher as view, along with kls, target, section and extra_context
        """
        if self.redirect:
            # Redirect overrides other options
            return self.redirect_view(self.redirect)

        target = self.target
        if callable(target):
            # Target already a callable
            return target, self.extra_context

        if target:
            kls = self.get_view_kls()
            view = dispatcher
            kwargs = {}
            if self.extra_context:
                kwargs.update(self.extra_context)
            kwargs.update(dict(kls=kls, target=target))
            return view, kwargs

    def redirect_view(self, redirect):
        '''
            Return view to be used for redirection
            If url is relative, it will make it absolute by joining with request.path
            If no url, a 404 will be raised
        '''
        from django.views.generic import RedirectView
        from django.http import Http404

        class Redirector(RedirectView):
            """Our customization on the redirect view"""
            def get_redirect_url(self, **kwargs):
                url = self.url
                if callable(url):
                    url = url(self.request)

                if url is None:
                    raise Http404

                if not url.startswith('/'):
                    url = '%s%s' % (self.request.path, url)
                    url = regexes['multiSlash'].sub('/', url)

                return url

        # Return view that redirects, and extra_context
        return Redirector.as_view(url=redirect), self.extra_context

    def get_view_kls(self):
        '''Determine view kls by looking at module and kls'''
        if not self.kls and not self.module:
            # No view to be determined
            return None

        if self.kls is not None and type(self.kls) not in (str, unicode):
            # kls is already an object
            return self.kls

        kls = self.clean_module_name(self.kls)
        if not self.module:
            # No module, return kls as a string
            return kls

        if type(self.module) in (str, unicode):
            # Module is a string, concatenate with kls
            module = self.clean_module_name(self.module)
            return "%s.%s" % (module, kls)

        else:
            # Module is an object
            # getattr each part of kls from it
            result = self.module
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

    def clone(self, all=False, **kwargs):
        """
            Return a copy of this object with new options.
            It Determines current options, updates with new options
            And returns a new Options object with these options
        """
        passon = []
        for _, required in self.setters():
            passon.extend(required)

        if all:
            no_propogate = ()
        else:
            no_propogate = (
                  'alias', 'match', 'values', 'target', 'redirect'
                , 'promote_children', 'propogate_display'
                )

        # Make sure display doesn't propogate if propogate_display is False
        if not self.propogate_display:
            no_propogate += ('display', )

        values = dict((arg, getattr(self, arg)) for arg in passon if arg not in no_propogate)
        values.update(kwargs)

        cloned = Options()
        cloned.set_everything(**values)
        return cloned

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

    def has_permissions(self, user):
        '''Determine if user has permissions given these options'''
        needs_auth = self.needs_auth
        if not needs_auth:
            return True

        # Determine if user is authenticated
        authenticated = user.is_authenticated()
        if type(needs_auth) is bool:
            return authenticated
        else:
            def iterAuth():
                if type(needs_auth) in (list, tuple):
                    for auth in needs_auth:
                        yield auth
                else:
                    yield needs_auth

            return authenticated and all(user.has_perm(auth) for auth in iterAuth())

    def clean_module_name(self, name):
        '''
            * Remove dots from beginning and end of the string
            * Complain about spaces and non-ascii characters
        '''
        if name is None:
            return None

        while name.startswith('.'):
            name = name[1:]

        while name.endswith('.'):
            name = name[:-1]

        if ' ' in name:
            raise ConfigurationError("'%s' is not a valid import location (has spaces)" % name)

        for part in name.split('.'):
            if not regexes['valid_import'].match(part):
                raise ConfigurationError(
                    "'%s' is not a valid import location ('%s' isn't a valid variable name)" % (name, part)
                )

        return name
