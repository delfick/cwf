#!/usr/bin/evn python

import os, sys

def manager(location, get_paths=None):
    """
        Custom version of the manage.py script that django provides

        It determines the package where you have your configuration and imports it before importing settings
            This is incase you have a custom import loader that does anything funky.
            Like pretending settings.py exists when it doesn't
        
        This function also accepts a function, that is given the name of your project.
            The function should then return a list of any extra paths to give to sys.path
    """
    import sys
    import os
    
    # Find the project and set DJANGO_SETTINGS_MODULE
    project = location.split(os.sep)[-1]
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project
    
    # Extend sys.path
    if get_paths and callable(get_paths):
        sys.path = get_paths(project, ignoreMissing=True) + sys.path
    
    # Start django
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

def main():
    if 'WEBLIBS' in os.environ:
        sys.path.insert(0, os.environ['WEBLIBS'])

    get_path = None
    try:
        from wsgibase import get_path
    except ImportError:
        pass

    manager(os.getcwd(), get_path)

if __name__ == '__main__':
    main()
