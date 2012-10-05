from django.conf.urls.defaults import include as django_include

class PatternList(object):
    """
        Encapsulate logic in creating a pattern_list
    """
    def __init__(self, section, stop_at=None, include_as=None, without_include=False):
        self.section = section
        self.include_as = include_as
        self.without_include = without_include

        if stop_at is None:
            stop_at = self.section
        self.stop_at = stop_at

    def __iter__(self):
        return self.pattern_list()

    def pattern_list(self):
        """Return list of url patterns for this section and its children"""
        for item in self.section.url_children:
            pattern_list = PatternList(item.section, stop_at=self.stop_at, include_as=item.include_as)
            for pattern_tuple in self.pattern_list_for(item, pattern_list):
                yield pattern_tuple

    def pattern_list_for(self, item, pattern_list):
        """
            Determine all pattern_tuples given an Item and associated PatternList object

            If item has an include_as and we haven't said without_include
                * yield path and django includer
            if item's section belongs to this pattern list
                * yield pattern_tuple from this pattern list
            Otherwise
                * yield all patterns from the pattern_list
        """
        if item.include_as is not None and not self.without_include:
            path, includer_options = pattern_list.pattern_tuple_includer()
            yield path, django_include(*includer_options)

        elif item.section is self.section:
            pattern_tuple = pattern_list.pattern_tuple()
            if pattern_tuple:
                yield pattern_tuple
        else:
            for pattern_tuple in pattern_list:
                yield pattern_tuple

    def pattern_tuple(self):
        """Return arguments for django pattern object for this section"""
        pattern = self.create_pattern(self.determine_url_parts())
        view_info = self.url_view()
        if view_info:
            view, kwargs = view_info
            return (pattern, view, kwargs, self.section.name)

    def pattern_tuple_includer(self):
        """Yield path and arguments for django include for this section"""
        path = "^{}/".format(self.include_as)
        options = self.section.url_options
        return path, (self.section.patterns(without_include=True), options.namespace, options.app_name)

    ########################
    ###   URL UTILITY
    ########################

    def create_pattern(self, url_parts):
        """Use create_pattern on section.url_options to create a url pattern"""
        return self.section.url_options.create_pattern(url_parts)

    def url_view(self):
        """Return (view, kwargs) for this section"""
        view_info = self.section.url_options.url_view(self.section)
        if view_info:
            view, kwargs = view_info
            view = self.section.make_view(view, self.section)
            return view, kwargs

    def url_part(self):
        """Get url part for this section"""
        part = self.section.url
        match = self.section.url_options.match
        if match:
            part = "(?P<%s>%s)" % (match, part)

        return part

    def determine_url_parts(self):
        """Get list of patterns making the full pattern for this section"""
        if not hasattr(self, '_url_parts'):
            if self.include_as is None:
                url_parts = self.parent_url_parts()
            else:
                url_parts = [self.include_as]

            url_part = self.url_part()
            if url_part != "":
                url_parts.append(url_part)
            self._url_parts = url_parts
        return self._url_parts

    def parent_url_parts(self):
        """Get url_parts from parent"""
        parts = []
        if self.section.parent and not self.section is self.stop_at:
            # Get parent patterns
            parts = PatternList(self.section.parent, stop_at=self.stop_at).determine_url_parts()
        return parts
