from django.utils.encoding import force_unicode
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
        return condition

    @property
    def has_permissions(self):
        '''Determine if user has permissions for this section'''
        user = self._request.user

        # Super user needs not ask for permissions
        if user.is_superuser:
            return True

        if self.needs_super_user:
            # Only get here if not super user
            return False

        # Don't care about authorisation if we don't need to
        needs_auth = self.needs_auth
        if not needs_auth:
            return True

        return self.has_auth(user, needs_auth)

    def has_auth(self, user, auth):
        """
            Determine if user has specified authentication
            If auth is boolean, return whether.is_authenticated()

            Otherwise determine if use.has_perm(auth)
            Where if auth is a list or tuple, all items in that are checked
        """
        if type(auth) is bool:
            return user.is_authenticated()

        # Find all the permissions to look for and check against
        def iter_auth():
            """Helper to determine the auths to look for"""
            if type(auth) in (list, tuple):
                for perm in auth:
                    yield perm
            else:
                yield auth
        return all(user.has_perm(auth) for auth in iter_auth())

########################
###   SINGLE
########################

class ButtonProperties(object):
    def __init__(self, kwargs):
        if kwargs is None:
            kwargs = {}

        if kwargs.get("for_all", False):
            kwargs['save_on_click'] = False

        defaults = dict(
            [ ('kls', None)
            , ('display', True)
            , ('for_all', False)
            , ('condition', None)
            , ('new_window', False)
            , ('needs_auth', None)
            , ('description', None)
            , ('save_on_click', True)
            , ('return_to_form', False)
            , ('need_super_user', True)
            ]
        )

        # Avoid custom setattr in __init__
        object.__setattr__(self, '_kwargs', kwargs)
        object.__setattr__(self, '_defaults', defaults)

    def __getattr__(self, key):
        """
            Get attribute from defaults
            Unless attribute is in kwargs
        """
        if key.startswith("_"):
            return object.__getattribute__(self, key)

        if key in self._kwargs:
            return self._kwargs[key]
        else:
            if key not in self._defaults:
                raise AttributeError(key)

            return self._defaults[key]

    def __setattr__(self, key, val):
        """Set attribute in kwargs"""
        if key.startswith("_"):
            object.__setattr__(self, key, val)
        else:
            self._kwargs[key] = val

class ButtonBase(object):
    def __getattr__(self, key):
        """Proxy to self.properties if key not on self"""
        if key.startswith('_'):
            return object.__getattribute__(self, key)

        if key in self.__dict__:
            return object.__getattribute__(self, key)
        else:
            properties = object.__getattribute__(self, 'properties')
            return getattr(properties, key)

    def __setattr__(self, key, val):
        """
            Set attribute on self
            unless attribute exists on properties, in which case set it there.
        """
        try:
            current = object.__getattribute__(self, key)
            object.__setattr__(self, key, val)
        except AttributeError:
            properties = object.__getattribute__(self, 'properties')
            if hasattr(properties, key):
                object.__setattr__(properties, key, val)
            else:
                object.__setattr__(self, key, val)

    @property
    def properties(self):
        if not hasattr(self, "_properties"):
            # Need properties for normal setattr to work
            kwargs = None
            if hasattr(self, 'kwargs'):
                kwargs = object.__getattribute__(self, 'kwargs')
            object.__setattr__(self, '_properties', ButtonProperties(kwargs))
        return self._properties

########################
###   BUTTON
########################

class Button(ButtonBase):
    group = False
    def __init__(self, url, desc, **kwargs):
        # Avoid custom setattr in __init__
        object.__setattr__(self, 'url', url)
        object.__setattr__(self, 'desc', desc)
        object.__setattr__(self, 'kwargs', kwargs)

    def title(self, obj):
        """
            Title is the description of the button
            Plus the unicode of the object if we are per instance
        """
        title = "{}".format(self.description)
        if not self.for_all:
            title = "{}: {}".format(title, force_unicode(obj))
        return title

    @property
    def html(self):
        if not hasattr(self, "_html"):
            self._html = self.determine_html()
        return self._html

    def copy_for_request(self, request, original=None):
        """Set request and original on the button"""
        return ButtonWrap(self, request, original)

    def determine_html(self):
        """Determine if we want an <input> or just an <a>"""
        if not self.save_on_click or self.for_all:
            link = self.link_as_anchor()
        else:
            link = self.link_as_input()
        return mark_safe(link)

    def link_as_input(self):
        return u'<input type="submit" name="tool_%s" value="%s"/>' % (self.url, self.desc)

    def link_as_anchor(self):
        url = self.url
        if self.save_on_click or not self.url.startswith('/'):
            url = "tool_%s" % self.url

        options = []
        if self.kls:
            options.append(u'class="%s"' % self.kls)

        if self.new_window:
            options.append(u'target="_blank"')

        return u'<a href="%s" %s>%s</a>' % (url, ' '.join(options), self.desc)

########################
###   GROUP
########################

class ButtonGroup(ButtonBase):
    group = True
    def __init__(self, name, buttons, **kwargs):
        # Avoid custom setattr in __init__
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'buttons', buttons)
        object.__setattr__(self, 'kwargs', kwargs)

    def copy_for_request(self, request, original=None):
        """Return a button group with all it's buttons wrapped in a button wrap"""
        buttons = [b.copy_for_request(request, original) for b in self.buttons]
        return ButtonGroup(self.name, buttons)

    @property
    def show(self):
        """Only show if we can show any of the buttons"""
        return any(button.show for button in self.buttons)
