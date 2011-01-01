#!/bin/sh
#Put this in your bash path and you don't need a manage.py file
python -c "
import os, sys
sys.path.insert(0, os.environ['WEBLIBS'])
from cwf.helpers.manage import manager
from wsgibase import getPath
manager(os.getcwd(), getPath)" $@
