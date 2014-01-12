from django.core.handlers.wsgi import WSGIHandler
from django.views import debug

from paste.debug.prints import PrintDebugMiddleware
from werkzeug import run_simple

import os

class Debugger(object):
    """
        Object to setup and start a Debugger instance of your site
    """
    default_port = 8000
    default_host = '0.0.0.0'

    def __init__(self, project=None, host=None, port=None, setup_project=None, project_options=None):
        self.host = host or self.default_host
        self.port = port or self.default_port
        self.project = project
        self._setup_project = setup_project
        self.project_options = project_options

    ########################
    ###   RUNNER
    ########################

    def run(self):
        """Start the debugger"""
        def setup_func():
            self.setup_500()
            self.setup_path(self.project)
        app = self.setup_app()
        try:
            run_simple(self.host, self.port, app
                , use_debugger=True, use_reloader=True, setup_func=setup_func
                )
        except TypeError as error:
            if error.message == "run_simple() got an unexpected keyword argument 'setup_func'":
                import traceback
                import sys
                traceback.print_exc()
                sys.exit("Please support https://github.com/mitsuhiko/werkzeug/issues/220")
            raise

    ########################
    ###   SETUP
    ########################

    def setup_app(self):
        """Create the application"""
        app = WSGIHandler()
        app = PrintDebugMiddleware(app)
        return app

    def setup_500(self):
        """Set 500 response"""
        def null_technical_500_response(request, exc_type, exc_value, tb):
            raise exc_type, exc_value, tb
        debug.technical_500_response = null_technical_500_response

    def setup_path(self, project):
        """Alter the path where to find the application"""
        os.environ['DJANGO_SETTINGS_MODULE'] = '{0}.settings'.format(project)
        kwargs = {}
        if self.project_options:
          kwargs = self.project_options
        self.setup_project(project, **kwargs)

    ########################
    ###   UTILITY
    ########################

    @property
    def setup_project(self):
        """
            Find function to setup the project with
            Use either _setup_project already on class
            Or Try to import <project>.project_setup

            If neither, use a function that does nothing
        """
        setup_project = self._setup_project
        if not setup_project:
            if setup_project and callable(setup_project):
                self._setup_project = setup_project
            else:
                self._setup_project = lambda project: None

        return self._setup_project
