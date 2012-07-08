from src.sections.section_master import SectionMaster

class Menu(object):
    """
        Object that knows about Section and SectionMaster
        To retrieve information necessary to create menus
    """
    def __init__(self, request, section):
        self.request = request
        self.section = section

        self.master = SectionMaster(self.request)

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

    def global_nav(self):
        """
            Return list of infos representing each top nav item
        """
        for child in self.section.root_ancestor().menu_sections:
            for info in self.master.get_info(child, self.path):
                yield info
