from django.core.handlers.wsgi import WSGIHandler
from django.views import debug

from werkzeug import run_simple, DebuggedApplication
from paste.debug.prints import PrintDebugMiddleware

import sys
import os

class Debugger(object):
    """
        Object to setup and start a Debugger instance of your site
    """
    def __init__(self, project=None, host=None, port=None, get_path=None):
        self.host = host
        self.port = port
        self.project = project
        self._get_path = get_path

    ########################
    ###   RUNNER
    ########################

    def run(self):
        """Start the debugger"""
        self.setup_500()
        self.setup_path(self.project)

        app = self.setup_app()
        run_simple(self.host, self.port, app, True)
    
    ########################
    ###   SETUP
    ########################

    def setup_app(self):
        """Create the application"""
        app = WSGIHandler()
        app = PrintDebugMiddleware(app)
        app = DebuggedApplication(app, True)

    def setup_500(self):
        """Set 500 response"""
        def null_technical_500_response(request, exc_type, exc_value, tb):
            raise exc_type, exc_value, tb
        debug.technical_500_response = null_technical_500_response

    def setup_path(self, project):
        """Alter the path where to find the application"""
        sys.path = self.get_path(project) + sys.path
        os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project
    
    ########################
    ###   UTILITY
    ########################

    @property
    def get_path(self):
        """
            Find function to modify sys.path with
            Use either _get_path already on class
            Or Try to import wsgibase.get_path

            If neither, use a function that just returns an empty list
        """
        if not self._get_path:
            get_path = None
            try:
                from wsgibase import get_path
            except ImportError:
                pass

            if not get_path or not callable(get_path):
                self._get_path = lambda project: []
        return self._get_path
