from django.utils.http import urlencode

import re

regexes = {
    'multi_slash' : re.compile('/+')
    }

class RedirectAddress(object):
    """
        Helper to determine where to redirect to.

        :param request: Object representing current Django request.
        :param address: String representing the address to modify into a redirect url
        :param relative: If we should be redirecting relative to the current page we're on
        :param carry_get: If we should use the GET parameters from the current request in our redirect
        :param ignore_get: List of GET parameters that should be ignored if carry_get is True
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
        """Returns the result of ``self.modify(unicode(self.address))``"""
        return self.modify(unicode(self.address))

    def modify(self, address):
        """
            Return a modified version of the address passed in as the redirect url.

            Uses the following methods in a pipeline of sorts (in this order):

            * :py:meth:`joined_address`
            * :py:meth:`strip_multi_slashes`
            * :py:meth:`add_get_params`
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
            Get base url from request.state if request has an attached ``state``.

            Otherwise, return ``request.META.get('SCRIPT_NAME', '')``
        """
        if hasattr(self.request, 'state'):
            return self.request.state.base_url
        else:
            return self.request.META.get('SCRIPT_NAME', '')

    @property
    def params(self):
        """
            Return dictionary of key value for GET params from ``self.request``.

            If not ``self.ignore_get`` then just return ``request.GET``

            Otherwise, return ``request.GET`` minus any values whose key is in ``self.ignore_get``
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
            If ``self.carry_get`` is False, then just return the address as is.

            Otherwise, urlencode the result of :py:attr:`params` and
            return a string that joins address and the parameters.
        """
        if not self.carry_get:
            return address

        params = urlencode(self.params)
        return "%s?%s" % (address, params)

    def joined_address(self, address):
        """
            If address is a :py:meth:`root_url`, then :py:meth:`join <url_join>` the address with base_url.

            Otherwise, if ``self.relative``, then :py:meth:`join <url_join>` the address with ``self.request.path``

            If the address is not a root url and ``self.relative`` is False, then return as is
        """
        if self.root_url(address):
            address = self.url_join(self.base_url, address)

        elif self.relative:
            address = self.url_join(self.request.path, address)

        return address

    def url_join(self, a, b):
        """Helper to join two urls such that there is only one ``/`` between them."""
        if not a or not b:
            return '%s%s' % (a, b)
        elif b[0] == '/' or a[-1] == '/':
            return '%s%s' % (a, b)
        else:
            return '%s/%s' % (a, b)
