"""
    Configuration specific to project
"""
import sys
import os

this_dir = os.path.abspath(os.path.dirname(__file__))
docs_dir = os.path.join(this_dir, '..')
sys.path.append(docs_dir)
from support.conf import *

copyright = u'2012, Stephen Moore'
project = u'CWF Documentation'

version = '0.1'
release = '0.1'
