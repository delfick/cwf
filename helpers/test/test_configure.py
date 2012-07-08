# coding: spec

from django.contrib import admin
from django.conf.urls.defaults import *

import sys
import os

thisDir = os.sep.join(__file__.split(os.sep)[:-1])
sys.path.append(thisDir)

from helpers import configure, P

class FakeSettings(object): pass
settings = FakeSettings()
configure(settings, 'example2'
      , P("part1")
      , P("part2")
      , P("part3", base=True)
      , prefix = "cwf.helpers.test"
      , includeDefaultUrls = True
      )

describe 'helpers', TestCase:
    urls = 'example2.urls'

    def checkLengths(self, site, info=None, base=None, menu=None):
        if info:
            len(site.info) |should| be(info)
        
        if base:
            len(site.base) |should| be(base)
        
        if menu:
            [m for m in site.menu()] |should| have(menu).sections
    
    def checkExists(self, *paths, **kwargs):
        desired = kwargs.get('desired', 200)
        for path in paths:
            res = self.client.get(path)
            st = res.status_code
            st |should| equal_to(desired)
        
    it 'should be able to get all models':
        from example2.models import Part1Model, Part2Model
        # If that doesn't raise an importError, then the test passes
        True |should| be(True)
        
    it 'should auto add all the admin':
        from example2.models import Part1Model, Part2Model
        admin.site._registry |should| include_all_of([Part1Model, Part2Model])
        
    it 'should be able to make a site object':
        from example2.urls import site, urlpatterns
        urlpatterns |should| have(3).patterns
        self.checkLengths(site, info=2, base=1, menu=3)
    
    it 'should be possible to follow the url scheme':
        self.checkExists(
              '', '/', '/part1/', '/part1/some/', '/part1/some/meh/', '/part2/apart/'
            , desired = 200
            )
    
    it 'should give 404 for urls that arent part of the scheme':
        self.checkExists(
              'asdf', '/asdf'
            , '/part2/apartd', '/part2/apart/d'
            , desired = 404
            )
