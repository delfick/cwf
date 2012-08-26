#!/bin/sh
# Put this in your bash path and you don't need a manage.py file
# Will add os.environ['WEBLIBS'] to the start of your sys.path
# Then assume cwf is in your path
# If it can do 'from wsgibase import get_path' then get_path is passed into manager
# The manager will use this function to determine what it prepends sys.path with
python -c "
import os, sys
if 'WEBLIBS' in os.environ:
    sys.path.insert(0, os.environ['WEBLIBS'])
from cwf.splitter.manager import manager
try:
    from wsgibase import get_path
except ImportError:
    get_path = None
manager(os.getcwd(), get_path)" $@
