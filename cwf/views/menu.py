from cwf.sections.section_master import SectionMaster
from rendering import renderer

class Menu(object):
    """
        Knows how to get the information required to render the
        navigation from a :ref:`section <sections_index>`.

        Assumes a top nav with one selected item.

        And a side nav that is everything under the selected top nav item
    """
    def __init__(self, request, section):
        self.request = request
        self.section = section

        self.master = SectionMaster(self.request)

    def global_nav(self):
        """
            Find the root ancestor of the current section and return a list of
            navs for just the top level sections.
        """
        if not hasattr(self, '_global_nav'):
            self._global_nav = list(self.navs_for(self.section.root_ancestor().menu_children))
        return self._global_nav

    def side_nav(self):
        """
            Find the top nav of the current section and return the list of navs
            representing the children for that top nav.

            These children will recursively have ``children`` of their own that
            will go as far down as the section itself and any siblings of this
            sections' parent.
        """
        if not hasattr(self, '_side_nav'):
            selected = self.selected_top_nav
            if selected:
                self._side_nav = list(selected.children())
            else:
                self._side_nav = []
        return self._side_nav

    @property
    def selected_top_nav(self):
        """Get the selected top nav"""
        if not hasattr(self, '_selected_top_nav'):
            selected = None
            filtered = filter(lambda nav: nav.selected()[0], self.global_nav())
            if filtered:
                selected = filtered[0]

            self._selected_top_nav = selected

        return self._selected_top_nav

    @property
    def path(self):
        """
            Get and memoize path from the request
            Make sure no trailing or leading slashes
        """
        if not hasattr(self, "_path"):
            meta = self.request
            if hasattr(self.request, 'META'):
                meta = self.request.META
            path = meta['PATH_INFO']
            while path and path.startswith("/"):
                path = path[1:]
            while path and path.endswith("/"):
                path = path[:-1]
            self._path = path.split('/')
        return self._path

    def children_function_for(self, section, parent):
        """Return lambda to get menu for children of some section"""
        return lambda : self.navs_for(section.menu_children, parent=parent)

    def navs_for(self, items, parent=None):
        """
            Return list of infos representing each top nav item
        """
        for item in items:
            child = item.section
            include_as = item.include_as
            for info in self.master.get_info(child, include_as, self.path, parent=parent):
                info.setup_children(self.children_function_for(child, info), child.has_children)
                yield info

    def render(self, menu, template, ignore_children=False):
        """
            Turn a list of info objects into html using a particular template
            Menu is result of self.global_nav or self.side_nav
            Template is path to the template to use
        """
        extra = dict(menu=menu, children_template=template, ignore_children=ignore_children)
        return renderer.simple_render(template, extra)
