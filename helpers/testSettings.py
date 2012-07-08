from settings import *
INSTALLED_APPS += ('django_nose', )

from django.template import loader, Context, Template
from django.test import TestCase
from nose.tools import nottest

from should_dsl import *
import re

regexes = { 'liWithSubMenu' : re.compile('<li class="has_sub_menu">') 
          , 'selectedLi' : re.compile('<li class="selected">') 
          , 'normalLi'   : re.compile('<li>')
          , 'ul'         : re.compile('<ul>')
          }

class MenuTester(TestCase):
    def setUp(self):
        super(MenuTester, self).setUp()
        self.getSite()
        
    @nottest
    def render(self, menu, name, gen):
        extra = {'gen' : getattr(menu, gen)()}
        t = loader.get_template('menu/%s.html' % name)
        c = Context(extra)
        return t.render(c).replace('\t', '').replace('    ', '').replace('\n', '')

    @nottest
    def getSite(self, withReload=False):
        if not hasattr(self, 'urls'):
            import urls
            self.urls = urls
            self.site = urls.site
        
        elif withReload:
            self.site.reset()
            reload(self.urls)
    
    @nottest
    def checkRender(self, render, selected=None, normal=None, withSubMenu=None, ul=None):
        if selected:
            found = regexes['selectedLi'].findall(render)
            found |should| have(selected).selected_li
            
        if normal:
            found = regexes['normalLi'].findall(render)
            found |should| have(normal).normal_li
            
        if withSubMenu:
            found = regexes['liWithSubMenu'].findall(render)
            found |should| have(withSubMenu).li_with_submenu
            
        if ul:
            found = regexes['ul'].findall(render)
            found |should| have(ul).ul
    
    @nottest
    def find(self, render, selected=True, url='/', alias='Home', shouldHave=None):
        regex = '<li%(selected)s><a href="%(url)s">%(alias)s</a></li>'
        options = { 'selected' : ''
                  , 'url' : url
                  , 'alias' : alias
                  }
        
        if selected:
            options['selected'] = ' class="selected"'
        
        found = re.findall(regex % options, render)
        if shouldHave:
            found |should| have(shouldHave).specific_items
        
        return found

MenuTester.is_noy_spec = True
