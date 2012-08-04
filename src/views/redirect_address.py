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
        """Determine address to redirect to"""
        if self.root_url(address):
            address = self.url_join(self.base_url, address)

        elif self.relative:
            address = self.url_join(self.request.path, address)

        # Make sure address has no multiple slashes
        # And has GET params if required
        address = self.without_slashes(address)
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
            return self.request.state.baseUrl
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
            return request.GET

        params = {}
        for key, val in self.request.GET.items():
            if key not in ignore_get:
                params[key] = val
        return params
    
    ########################
    ###   UTILITY
    ########################

    def root_url(self, address):
        """Determine if address is a root url (starts with slash)"""
        return address[0] == '/'

    def without_slashes(self, string):
        """Strip slashes from a string"""
        return regexes['multi_slash'].sub('/', string)

    def add_get_params(self, address):
        """
            If carry_get is true then add get params from the request
            Otherwise just return address as is
        """
        if not self.carry_get:
            return address

        params = urlencode(self.params)
        return "%s?%s" % (address, params)

    def url_join(self, a, b):
        """Helper to join two urls"""
        if not a or not b:
            return '%s%s' % (a, b)
        elif b[0] == '/' and a[-1] != '/':
            return '%s%s' % (a, b)
        elif b[0] != '/' and a[-1] == '/':
            return '%s%s' % (a, b)
        else:
            return '%s/%s' % (a, b)
