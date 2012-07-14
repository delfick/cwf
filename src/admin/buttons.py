from django.utils.safestring import mark_safe

########################
###   WRAP
########################

class ButtonWrap(object):
    """Small object to hold button options along with the current request"""
    def __init__(self, button, request, original):
        self._button = button
        self._request = request
        self._original = original

    def __getattr__(self, key):
        """
            Proxy to self._button before self
            Unless key is prefixed with underscore
        """
        if key.startswith('_'):
            return object.__getattribute__(self, key)

        if hasattr(self._button, key):
            return getattr(self._button, key)
        else:
            return object.__getattribute__(self, key)

    @property
    def show(self):
        """Determine if the button should be shown for this request"""
        return self.display and self.has_permissions and not self.noshow

    @property
    def noshow(self):
        """Determine if there is any condition against been shown"""
        condition = self.condition
        if callable(condition):
            condition = condition(self._button, self._original)
        return not condition

    @property
    def has_permissions(self):
        '''Determine if user has permissions for this section'''
        user = self._request.user

        # Super user needs not ask for permissions
        if self.needSuperUser and not user.is_superuser:
            return False
        
        # Don't care about authorisation if we don't need to
        needs_auth = self.needs_auth
        if not needs_auth:
            return True
        
        if type(needsAuth) is bool:
            return user.is_authenticated()

        # Find all the permissions to look for and check against
        def iter_auth():
            """Helper to determine the auths to look for"""
            if type(needsAuth) in (list, tuple):
                for auth in needsAuth:
                    yield auth
            else:
                yield needsAuth
        return all(user.has_perm(auth) for auth in iter_auth())

########################
###   GROUP
########################

class ButtonGroup(object):
    group = True
    def __init__(self, name, buttons, **kwargs):
        self.name = name
        self.buttons = buttons

    def copy_for_request(self, request, original=None):
        """Return a button group with all it's buttons wrapped in a button wrap"""
        buttons = [ButtonWrap(b, request, original) for b in self.buttons]
        return ButtonGroup(self.name, buttons)

########################
###   SINGLE
########################

class Button(object):
    group = False
    def __init__(self, url, desc, **kwargs):
        self.url = url
        self.desc = desc

        # Set properties and cache html for this button
        self.setProperties(**kwargs)
        self.html = self.determine_html()

    def copy_for_request(self, request, original=None):
        """Set request and original on the button"""
        return ButtonWrap(self, request, original)

    def set_properties(self, **kwargs):
        """
            Set properties on the button
            Ensure sensible defaults
            And complain about unknown properties
        """
        known = dict(
            [ ('kls', None)
            , ('display', True)
            , ('for_all', False)
            , ('condition', None)
            , ('new_window', False)
            , ('needs_auth', None)
            , ('description', None)
            , ('save_on_click', True)
            , ('need_super_user', True)
            , ('execute_and_redirect', False)
            ]
        )

        # Make sure we don't have unexpected values
        leftover = set(kwargs.keys()) - set(known.keys())
        if leftover:
            raise Exception("Button doesn't know about some provided attributes: %s" % leftover)

        # Set attributes on the class
        for key, dflt in known.items():
            setattr(self, key, kwargs.get(key, dflt))

        # Set save_on_click to false if for_all
        if self.for_all:
            self.save_on_click = False
    
    def determine_html(self):
        """Determine if we want an <input> or just an <a>"""
        if not self.save_on_click or self.for_all:
            link = self.link_as_anchor()
        else:
            link = self.link_as_input()
        return mark_safe(link)

    def link_as_input(self):
        url = self.url
        if not url.endswith("/"):
            url = "%s/" % url
        return u'<input type="submit" name="tool_%s" value="%s"/>' % (url, self.desc)
    
    def link_as_anchor(self):
        url = self.url
        if self.save_on_click or not self.url.startswith('/'):
            url = "tool_%s" % self.url

        if not url.endswith("/"):
            url = "%s/" % url
        
        options = []
        if self.kls:
            options.append(u'class="%s"' % self.kls)
        
        if self.newWindow:
            options.append(u'target="_blank"')
        
        return u'<a href="%s" %s>%s</a>' % (url, ' '.join(options), self.desc)
