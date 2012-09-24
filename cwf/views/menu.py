from cwf.sections.section_master import SectionMaster
from rendering import renderer

class Menu(object):
    """
        Object that knows about Section and SectionMaster
        To retrieve information necessary to create menus

        Assumes a top nav with one selected item.
        And a side nav that is everything under the selected top nav item
    """
    def __init__(self, request, section):
        self.request = request
        self.section = section

        self.master = SectionMaster(self.request)

    def global_nav(self):
        return self.navs_for(self.top_nav, setup_children=False)

    def side_nav(self):
        selected = self.selected_top_nav
        if selected:
            return self.selected_top_nav.children()
        else:
            return []

    @property
    def top_nav(self):
        """Get all the top nav info objects"""
        if not hasattr(self, '_top_nav'):
            self._top_nav = list(self.navs_for(self.section.root_ancestor().menu_sections))
        return self._top_nav

    @property
    def selected_top_nav(self):
        """Get the selected top nav"""
        if not hasattr(self, '_selected_top_nav'):
            selected = None
            filtered = filter(lambda nav: nav.selected()[0], self.top_nav)
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
            path = self.request['PATH_INFO']
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
            for info in self.master.get_info(child, self.path, parent=parent):
                info.setup_children(self.children_function_for(child, info), child.has_children)
                yield info

    def render(self, menu, template):
        """
            Turn a list of info objects into html using a particular template
            Menu is result of self.global_nav or self.side_nav
            Template is path to the template to use
        """
        extra = dict(menu=menu, children_template=template)
        return renderer.simple_render(template, extra)
