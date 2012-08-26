#!/usr/bin/evn python

from manager import manager
import os, sys

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
