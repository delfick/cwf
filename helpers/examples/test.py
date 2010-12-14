# coding: spec

"""
An example test.py
"""

from cwf.menus import Menu

from testSettings import MenuTester
from main.active import parts

describe MenuTester 'Global Menu':
    it 'should make it when base is selected':
        from main.base.urls import base
        menu = Menu(self.site, [], base)
        result = self.render(menu, 'global', 'getGlobal')
        
        self.checkRender(result, selected=1, ul=1)
        self.find(result, selected=True, url='/', alias='Home', shouldHave=1)
        
    it 'should make it when something other than base is selected':
        from main.news.urls import nls
        menu = Menu(self.site, ['news'], nls.rootAncestor())
        result = self.render(menu, 'global', 'getGlobal')
        
        self.checkRender(result, selected=1, ul=1)
        self.find(result, selected=True, url='/news', alias='News', shouldHave=1)
             
