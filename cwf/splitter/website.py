from imports import inject
from parts import Parts

class Website(object):
    """
        Given a particular package and Part objects
        Insert <package>.<urls>, <package>.<models> and load all admin.

        Use like:
        website = Website(settings, 'main', Part(...), Part(...))
        website.configure()
    """
    def __init__(self, settings, package, *parts, **kwargs):
        self.parts = parts
        self.package = package
        self.settings = settings

        self.prefix = kwargs.get("prefix", None)
        self.include_default_urls = kwargs.get("include_default_urls", False)

    def configure(self):
        """
            Configure a website to exist in the package specified with the parts specified.
            This will inject into package.models and package.urls
            It will also import all admin logic
        """
        inject(self.urls, self.names_for("urls"))
        inject(self.models, self.names_for("models"))
        self.load_admin()

    @property
    def config(self):
        """
            Create a Parts objects from the parts specified
            And memoize it in settings.PARTCONFIG[package]
        """
        package = self.package
        settings = self.settings
        if not hasattr(settings, 'PARTCONFIG'):
            settings.PARTCONFIG = {}

        if package not in settings.PARTCONFIG:
            settings.PARTCONFIG[package] = Parts(package, *self.parts)
        return settings.PARTCONFIG[package]

    def load_admin(self):
        """Load all the admin for the parts specified"""
        self.config.load_admin()

    @property
    def models(self):
        """Return all models for this package"""
        return self.config.models()

    @property
    def urls(self):
        """Return a function to be uses as <package>.<urls>"""
        return lambda : self.config.urls(include_defaults=self.include_default_urls)

    def names_for(self, name):
        """
            Determine names to inject into for a particular name
            Uses <package>.<name>
            And if prefix was specified, <prefix>.<package>.<name>
        """
        names = ["%s.%s" % (self.package, name)]
        if self.prefix:
            names.append("%s.%s" % (self.prefix, names[0]))
        return names
