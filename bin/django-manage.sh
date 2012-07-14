#!/bin/sh
# Put this in your bash path and you don't need a manage.py file
# Will add os.environ['WEBLIBS'] to the start of your sys.path
# Then assume cwf is in your path
# And that 'from wsgibase import get_path' will work
python -c "
import os, sys
if 'WEBLIBS' in os.environ:
    sys.path.insert(0, os.environ['WEBLIBS'])
from cwf.splitter.manager import manager
from wsgibase import get_path
manager(os.getcwd(), get_path)" $@
