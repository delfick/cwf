#!/usr/bin/env python

from debugger import Debugger

import argparse
import sys
import os

def make_parser(self):
    """Create an argparser to get things from the CLI"""
    parser = argparse.ArgumentParser(description="Start debugger instance of your website")
    parser.add_argument("project"
        , help = "The project you want to start up"
        , required = True
        )

    parser.add_argument("-p", "--port"
        , help = "The port to run the website on"
        , type = int
        , default = Debugger.default_port
        )

    parser.add_argument("-h", "--host"
        , help = "The host to run the website on"
        , default = Debugger.default_host
        )

    return parser

def main(self, argv=None):
    """Popuplate options on the class from sys.argv"""
    if not argv:
        argv = sys.argv[1:]

    parser = self.make_parser()
    args = parser.parse_args(argv)

    Debugger(project=args.project, host=args.host, port=args.port).run()

if __name__ == '__name__':
    main()
