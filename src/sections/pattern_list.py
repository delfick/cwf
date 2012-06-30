class PatternList(object):
    """
        Encapsulate logic in creating a pattern_list
    """
    def __init__(self, section, start=True, stop_at=None):
        self.end = not section.has_children
        self.start = start
        self.section = section
        
        if stop_at is None:
            stop_at = self.section
        self.stop_at = stop_at
    
    def __iter__(self):
        return self.pattern_list()
    
    def pattern_list(self):
        """Return list of url patterns for this section and its children"""
        # Yield children
        for child in self.section.url_children:
            if child is self.section:
                yield self.pattern_tuple()
            else:
                for url_pattern in PatternList(child, start=False, stop_at=self.stop_at):
                    yield url_pattern
    
    def pattern_tuple(self):
        """Yield pattern list for this section"""
        pattern = self.create_pattern(self.determine_url_parts(), self.start, self.end)
        view, kwargs = self.url_view()
        return (pattern, view, kwargs, self.section.name)
        
    def include_path(self, include_as=None, start=False, end=False):
        """
            Determine path to this includer
            Will use self.url_pattern without trailing $
            unless include_as is specified which will override this
        """
        if not include_as:
            url_parts = self.determine_url_parts()
        else:
            while include_as.startswith("^"):
                include_as = include_as[1:]
            
            while include_as.endswith("/"):
                include_as = include_as[:-1]
            
            url_parts = [include_as]
        
        return self.create_pattern(url_parts, start=start, end=end)
        
    ########################
    ###   URL UTILITY
    ########################
    
    def create_pattern(self, url_parts, start, end):
        """Use create_pattern on section.options to create a url pattern"""
        return self.section.options.create_pattern(url_parts, start=start, end=end)
    
    def url_view(self):
        """Return (view, kwargs) for this section"""
        return self.section.options.url_view(self.section)
    
    def url_part(self):
        """Get url part for this section"""
        part = self.section.url
        match = self.section.options.match
        if match:
            part = "(?P<%s>%s)" % (match, part)
        
        return part

    def determine_url_parts(self):
        """Get list of patterns making the full pattern for this section"""
        if not hasattr(self, '_url_parts'):
            url_parts = self.parent_url_parts()
            url_parts.append(self.url_part())
            self._url_parts = url_parts
        return self._url_parts    
    
    def parent_url_parts(self):
        """Get url_parts from parent"""
        parts = []
        if self.section.parent and not self.section is self.stop_at:
            # Get parent patterns
            parts = PatternList(self.section.parent, stop_at=self.stop_at).determine_url_parts()
        return parts
