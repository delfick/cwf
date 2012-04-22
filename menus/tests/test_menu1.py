# coding: spec

from urls.section import Section, Site, Values
from menus import Menu

import fudge

describe 'Menu':
    before_each:
        self.site1 = Site('site1')
        self.site2 = Site('site2')
        self.site3 = Site('site3')
        
        self.sect1 = Section('a')
        self.sect1_1 = self.sect1.add('nice')
        self.sect1_1_1 = self.sect1_1.add('place')
        
        self.sect2 = Section('b')
        self.sect2_1 = self.sect2.add('bad')
        self.sect2_1_1 = self.sect2_1.add('road')
        
        self.sect3 = Section('c')
        self.sect3_1 = self.sect3.add('hello')
        self.sect3_1_1 = self.sect3_1.add('there')
        
        self.request = fudge.Fake("request")
        
        def getGiving(part, give):
            section, appear, fullUrl, alias, selected, children, options = part
            if give is None:
                giving = (section, appear, fullUrl, alias, selected)
                
            else:
                giving = []
                useTuple = True
                if type(give) is int:
                    useTuple = False
                    give = [give]
                    
                for p in give:
                    giving.append(part[p])
                
                if useTuple:
                    giving = tuple(giving)
                else:
                    giving = giving[0]
            
            return giving, children
            
        def layeredRoll(gen, give=None):
            parts = []
            if callable(gen):
                gen = gen()
            
            for part in gen:
                next = []
                for info in part:
                    giving, _ = getGiving(info, give)
                    next.append(giving)
                    
                parts.append(next)
            
            return parts
        
        def heirarchialRoll(gen, give=None):
            parts = []
            if callable(gen):
                gen = gen()
              
            for part in gen:
                giving, children = getGiving(part, give)
                childParts = heirarchialRoll(children, give)
                parts.append([giving] + childParts)
            
            return parts
    
        self.layeredRoll = layeredRoll
        self.heirarchialRoll = heirarchialRoll
    
    describe 'values':
        before_each:
            self.site1.add(self.sect3)
            
            self.sect3_1_1_1 = self.sect3_1_1.add('\d+').base(''
                , values = Values(
                    lambda (r, pu, p) : pu[1:] + ['asdf'] + p
                  , lambda (r, pu, p), value : ('%s%s' % (pu[-1], value), value)
                  , asSet=False
                  )
                )
        
        describe 'heirarchially':
            it 'should give values function parenturl and path':
                menu = Menu(self.request, self.site1, ['c', 'hello', 'there'], self.sect3)
                self.heirarchialRoll(menu.heirarchial(), give=[0, 3, 2]) | should.equal_to | [
                    [ (self.sect3_1, 'Hello', ['', 'c', 'hello'])
                    , [ (self.sect3_1_1, 'There', ['', 'c', 'hello', 'there']) 
                      , [ (self.sect3_1_1_1, 'therec', ['', 'c', 'hello', 'there', 'c']) ]
                      , [ (self.sect3_1_1_1, 'therehello', ['', 'c', 'hello', 'there', 'hello']) ]
                      , [ (self.sect3_1_1_1, 'therethere', ['', 'c', 'hello', 'there', 'there']) ]
                      , [ (self.sect3_1_1_1, 'thereasdf', ['', 'c', 'hello', 'there', 'asdf']) ]
                      ]
                    ]
                ]
                
            it 'should give values function parenturl and path':
                menu = Menu(self.request, self.site1, ['c', 'hello', 'there', 'blah', 'meh'], self.sect3)
                self.heirarchialRoll(menu.heirarchial(), give=[0, 3, 2]) | should.equal_to | [
                    [ (self.sect3_1, 'Hello', ['', 'c', 'hello'])
                    , [ (self.sect3_1_1, 'There', ['', 'c', 'hello', 'there']) 
                      , [ (self.sect3_1_1_1, 'therec', ['', 'c', 'hello', 'there', 'c']) ]
                      , [ (self.sect3_1_1_1, 'therehello', ['', 'c', 'hello', 'there', 'hello']) ]
                      , [ (self.sect3_1_1_1, 'therethere', ['', 'c', 'hello', 'there', 'there']) ]
                      , [ (self.sect3_1_1_1, 'thereasdf', ['', 'c', 'hello', 'there', 'asdf']) ]
                      , [ (self.sect3_1_1_1, 'thereblah', ['', 'c', 'hello', 'there', 'blah']) ]
                      , [ (self.sect3_1_1_1, 'theremeh', ['', 'c', 'hello', 'there', 'meh']) ]
                      ]
                    ]
                ]
        
        describe 'layered':
            it 'should give values function parenturl and path':
                menu = Menu(self.request, self.site1, ['c', 'hello', 'there'], self.sect3)
                self.layeredRoll(menu.layered(), give=[0, 3, 2]) | should.equal_to | [
                      [ (self.sect3_1, 'Hello', ['', 'c', 'hello']) ]
                    , [ (self.sect3_1_1, 'There', ['', 'c', 'hello', 'there']) ]
                    , [ 
                        (self.sect3_1_1_1, 'therec', ['', 'c', 'hello', 'there', 'c'])
                      , (self.sect3_1_1_1, 'therehello', ['', 'c', 'hello', 'there', 'hello'])
                      , (self.sect3_1_1_1, 'therethere', ['', 'c', 'hello', 'there', 'there'])
                      , (self.sect3_1_1_1, 'thereasdf', ['', 'c', 'hello', 'there', 'asdf'])
                      ]
                    ]
                
            it 'should give values function parenturl and path':
                menu = Menu(self.request, self.site1, ['c', 'hello', 'there', 'blah', 'meh'], self.sect3)
                self.layeredRoll(menu.layered(), give=[0, 3, 2]) | should.equal_to | [
                      [ (self.sect3_1, 'Hello', ['', 'c', 'hello']) ]
                    , [ (self.sect3_1_1, 'There', ['', 'c', 'hello', 'there']) ]
                    , [ 
                        (self.sect3_1_1_1, 'therec', ['', 'c', 'hello', 'there', 'c'])
                      , (self.sect3_1_1_1, 'therehello', ['', 'c', 'hello', 'there', 'hello'])
                      , (self.sect3_1_1_1, 'therethere', ['', 'c', 'hello', 'there', 'there'])
                      , (self.sect3_1_1_1, 'thereasdf', ['', 'c', 'hello', 'there', 'asdf'])
                      , (self.sect3_1_1_1, 'thereblah', ['', 'c', 'hello', 'there', 'blah'])
                      , (self.sect3_1_1_1, 'theremeh', ['', 'c', 'hello', 'there', 'meh'])
                      ]
                    ]
            
    describe 'Global menu':
        it 'should give an empty list if no sections':
            menu = Menu(self.request, self.site1, [''])
            [t for t in menu.getGlobal()] | should.equal_to | []
        
        it 'should give a list of sections in the site that are in the menu':
            self.site2.add(self.sect1, base=True, inMenu=True)
            
            self.site1.add(self.sect2, inMenu=True)
            self.site1.add(self.sect3, inMenu=False)
            self.site1.add(site=self.site2, inMenu=True)
            
            menu = Menu(self.request, self.site1, [''])
            [t[0] for t in menu.getGlobal()] | should.equal_to | [self.sect2, self.sect1]
        
        it 'should give base section first':
            self.site2.add(self.sect1, base=True, inMenu=True)
            
            self.site1.add(self.sect2, inMenu=True)
            self.site1.add(site=self.site2, inMenu=True)
            self.site1.add(self.sect3, inMenu=True, base=True)
            
            menu = Menu(self.request, self.site1, [''])
            [t[0] for t in menu.getGlobal()] | should.equal_to | [self.sect3, self.sect2, self.sect1]
    
    describe 'nav menus': pass
            
        describe '___heirarchial':
            before_each:
                self.roll = self.heirarchialRoll
                
                base = self.site1.makeBase().base(showBase=False)
                base.adopt(self.sect1, self.sect2, self.sect3)
                
                self.sect2_1_1.base(
                    values = Values( ['1', '2', '3']
                                   , lambda (r, pu, p), value : ('_%s' % value, '%s_' % value)
                                   , asSet=False
                                   )
                )
                
                self.menu = lambda path : Menu(self.request, self.site1, path, base)
            
            it 'should work on a site object with no base or children':
                menu = Menu(self.request, self.site3, [], None)
                self.roll(menu.heirarchial(), give=0) | should.equal_to | []
            
            it 'should work on a site object with no base':
                sect = Section('blah')
                self.site3.add(sect)
                
                menu = Menu(self.request, self.site3, [], sect)
                self.roll(menu.heirarchial(includeFirst=True), give=0) | should.equal_to | [[sect]]
                
            it 'should give info heirarchially':
                menu = self.menu([])
                self.roll(menu.heirarchial(), give=0) | should.equal_to | [
                      [ self.sect1
                      , [ self.sect1_1
                        , [ self.sect1_1_1 ]
                        ]
                      ]
                    , [ self.sect2
                      , [ self.sect2_1
                        , [ self.sect2_1_1 ]
                        , [ self.sect2_1_1 ]
                        , [ self.sect2_1_1 ]
                        ]
                      ]
                    , [ self.sect3
                      , [ self.sect3_1
                        , [ self.sect3_1_1 ]
                        ]
                      ]
                ]
                
            it 'should determine fullUrl properly':
                menu = self.menu(['a', 'nice'])
                self.roll(menu.heirarchial(), give=2) | should.equal_to | [
                      [ ['', 'a']
                      , [ ['', 'a', 'nice']
                        , [ ['', 'a', 'nice', 'place'] ]
                        ]
                      ]
                    , [ ['', 'b']
                      , [ ['', 'b', 'bad']
                        , [ ['', 'b', 'bad', '1_'] ]
                        , [ ['', 'b', 'bad', '2_'] ]
                        , [ ['', 'b', 'bad', '3_'] ]
                        ]
                      ]
                    , [ ['', 'c']
                      , [ ['', 'c', 'hello']
                        , [ ['', 'c', 'hello', 'there'] ]
                        ]
                      ]
                ]
                
            it 'should determine alias properly':
                menu = self.menu(['a', 'nice'])
                self.roll(menu.heirarchial(), give=3) | should.equal_to | [
                      [ 'A'
                      , [ 'Nice'
                        , [ 'Place' ]
                        ]
                      ]
                    , [ 'B'
                      , [ 'Bad'
                        , [ '_1' ]
                        , [ '_2' ]
                        , [ '_3' ]
                        ]
                      ]
                    , [ 'C'
                      , [ 'Hello'
                        , [ 'There' ]
                        ]
                      ]
                ]
                
            it 'should determine selection properly_1':
                menu = self.menu(['b', 'bad', '2_'])
                self.roll(menu.heirarchial(), give=4) | should.equal_to | [
                      [ False
                      , [ False
                        , [ False ]
                        ]
                      ]
                    , [ True
                      , [ True
                        , [ False ]
                        , [ True ]
                        , [ False ]
                        ]
                      ]
                    , [ False
                      , [ False
                        , [ False ]
                        ]
                      ]
                ]
                
            it 'should determine selection properly_2':
                menu = self.menu(['a', 'nice'])
                self.roll(menu.heirarchial(), give=4) | should.equal_to | [
                      [ True
                      , [ True
                        , [ False ]
                        ]
                      ]
                    , [ False
                      , [ False
                        , [ False ]
                        , [ False ]
                        , [ False ]
                        ]
                      ]
                    , [ False
                      , [ False
                        , [ False ]
                        ]
                      ]
                ]
            
        describe '___layered':
            before_each:
                self.roll = self.layeredRoll
                
                base = self.site1.makeBase().base(showBase=False)
                base.adopt(self.sect1, self.sect2, self.sect3)
                
                self.sect2_1_1.base(
                    values = Values( ['1', '2', '3']
                                   , lambda (r, pu, p), value : ('_%s' % value, '%s_' % value)
                                   , asSet=False
                                   )
                )
                
                self.menu = lambda path : Menu(self.request, self.site1, path, base)
            
            it 'should work on a site object with no base or children':
                menu = Menu(self.request, self.site3, [], None)
                self.roll(menu.layered(), give=0) | should.equal_to | []
            
            it 'should work on a site object with no base':
                sect = Section('blah')
                self.site3.add(sect)
                
                menu = Menu(self.request, self.site3, [], sect)
                self.roll(menu.layered(includeFirst=True), give=0) | should.equal_to | [[sect]]
            
            it 'should give info layered only for selected sections':
                menu = self.menu([])
                self.roll(menu.layered(), give=0) | should.equal_to | [
                      [ self.sect1, self.sect2, self.sect3 ]
                ]
                
            it 'should determine fullUrl properly':
                menu = self.menu(['b', 'bad', '2_'])
                self.roll(menu.layered(), give=2) | should.equal_to | [
                      [ ['', 'a'], ['', 'b'], ['', 'c'] ]
                    , [ ['', 'b', 'bad'] ]
                    , [ ['', 'b', 'bad', '1_'], ['', 'b', 'bad', '2_'], ['', 'b', 'bad', '3_'] ]
                ]
                
            it 'should determine alias properly':
                menu = self.menu(['b', 'bad', '2_'])
                self.roll(menu.layered(), give=3) | should.equal_to | [
                      [ 'A', 'B', 'C' ]
                    , [ 'Bad' ]
                    , [ '_1', '_2', '_3' ]
                ]
                
            it 'should determine selection properly_1':
                menu = self.menu(['b', 'bad', '2_'])
                self.roll(menu.layered(), give=4) | should.equal_to | [
                      [ False, True, False ]
                    , [ True ]
                    , [ False, True, False ]
                ]
                
            it 'should determine selection properly_2':
                menu = self.menu(['a', 'nice'])
                self.roll(menu.layered(), give=4) | should.equal_to | [
                      [ True, False, False ]
                    , [ True ]
                    , [ False ]
                ]
                
                
                
                
