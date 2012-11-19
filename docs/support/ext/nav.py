"""
    Code to inject necessary information into each page
    Such that a navigation can be generated for each page.

    See support/navigation.py for the content of the navigation
"""
from navigation import toplinks as specification
import os
import re

class TopNav(object):
    def __init__(self):
        self.toplinks = [
            (name, url, re.compile(condition))
            for (name, url, condition) in specification
        ]

    def path_for(self, url, pagename):
        """Path for url relative to pagename"""
        parts = pagename.split('/')[:-1]
        if len(parts) == 0:
            return url[1:]
        return os.path.relpath(url, '/%s' % '/'.join(parts))
    
    def moreContext(self, app, pagename, templatename, context, doctree):
        """
            Put toplinks into the context
            As a list of (name, url, selected) tuples

            Where name is the name to give the link
            url is the location to point the link to
            selected is a boolean saying whether this page is selected or not
        """
        links = []
        for name, url, condition in self.toplinks:
            link = self.path_for(url, pagename)
            links.append((name, link, condition.match(pagename)))

        context['toplinks'] = links

def setup(app):    
    app.connect("html-page-context", TopNav().moreContext)
