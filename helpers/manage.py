def manager(location, getPaths=None):
    """Custom version of the manage.py script that django provides
    It determines the package where you have your configuration and imports it before importing settings
        This is incase you have a custom import loader that does anything funky.
        Like pretending settings.py exists when it doesn't
    This function also accepts a function, that is given the name of your project.
        The function should then return a list of any extra paths to give to sys.path
    """
    import sys
    import os
    
    project = location.split(os.sep)[-1]
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project
    
    from django.core.management import execute_manager
    if getPaths:
        sys.path = getPaths(project, ignoreMissing=True) + sys.path
    # Import the site so that any funky loading can happen in __init__.py
    # For example, making django think there is a settings.py when there isn't.
    __import__(project, globals(), locals(), [], -1)
    try:
        import settings # Assumed to be in the same directory.
    except ImportError:
        import sys
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)
    
    execute_manager(settings)
        
