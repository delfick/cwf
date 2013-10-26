#!/usr/bin/evn python

import os, sys

def setup_project(project, expected=False, **kwargs):
    """If project has a project_setup function, then execute it"""
    project_setup = None
    try:
        imported = __import__(project, globals(), locals(), ['project_setup'], -1)
        project_setup = getattr(imported, 'project_setup', None)
    except ImportError:
        if expected:
            raise
        pass

    if project_setup:
        project_setup(**kwargs)

def manager(project):
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
    os.environ['DJANGO_SETTINGS_MODULE'] = '{0}.settings'.format(project)
    setup_project(project)

    # Start django
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

def main():
    project = os.getcwd().split(os.sep)[-1]
    manager(project)

if __name__ == '__main__':
    main()
