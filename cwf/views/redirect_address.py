from django.utils.http import urlencode

import re

regexes = {
    'multi_slash' : re.compile('/+')
    }

class RedirectAddress(object):
    """
        Helper to determine where to redirect to
        Given a request and address and some other options
    """
    def __init__(self, request, address, relative=True, carry_get=False, ignore_get=None):
        self.request = request
        self.address = address
        self.relative = relative
        self.carry_get = carry_get
        self.ignore_get = ignore_get

    ########################
    ###   USAGE
    ########################

    @property
    def modified(self):
        """Return modified version of unicode(self.address)"""
        return self.modify(unicode(self.address))

    def modify(self, address):
        """
            Determine address to redirect to
            * Join address with either base_url or request.path as necessary
            * Make sure address has no multiple slashes
            * And has GET params if required
        """
        address = self.joined_address(address)
        address = self.strip_multi_slashes(address)
        address = self.add_get_params(address)

        return address

    ########################
    ###   GETTERS
    ########################

    @property
    def base_url(self):
        """
            Get base url from request.state
            Or from request.META if request has no state
        """
        if hasattr(self.request, 'state'):
            return self.request.state.base_url
        else:
            return self.request.META.get('SCRIPT_NAME', '')

    @property
    def params(self):
        """
            Return dictionary of key value for GET params from request
            If not any ignoreable keys then just return request.GET
            Otherwise return dict with everything in request.GET except things in ignoreable
        """
        if not self.ignore_get:
            return self.request.GET

        params = {}
        for key, val in self.request.GET.items():
            if key not in self.ignore_get:
                params[key] = val
        return params

    ########################
    ###   UTILITY
    ########################

    def strip_multi_slashes(self, string):
        """Replace multiple slashes with single slashes in a string"""
        return regexes['multi_slash'].sub('/', string)

    def root_url(self, address):
        """Determine if address is a root url (starts with slash)"""
        return address[0] == '/'

    def add_get_params(self, address):
        """
            If carry_get is true then add get params from the request
            Otherwise just return address as is
        """
        if not self.carry_get:
            return address

        params = urlencode(self.params)
        return "%s?%s" % (address, params)

    def joined_address(self, address):
        """
            If address is a root address then join with base_url
            If self.redirect then get address releative to the path of the request
            Otherwise just return address
        """
        if self.root_url(address):
            address = self.url_join(self.base_url, address)

        elif self.relative:
            address = self.url_join(self.request.path, address)

        return address

    def url_join(self, a, b):
        """Helper to join two urls"""
        if not a or not b:
            return '%s%s' % (a, b)
        elif b[0] == '/' or a[-1] == '/':
            return '%s%s' % (a, b)
        else:
            return '%s/%s' % (a, b)
