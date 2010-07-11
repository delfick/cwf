# coding: spec

from urls.section import Site, Section

describe 'Site':
    before_each:
        self.site = Site('test')
        self.sect1 = Section('some', name='sect1')
        self.sect2 = Section('very', name='sect2')
        self.sect3 = Section('nice', name='sect3')
        self.sect4 = Section('place', name='sect4')
        
        for sect in [self.sect1, self.sect2, self.sect3, self.sect4]:
            sect.add('meh')
            
        self.site2 = Site('testing')
        sect1 = Section('meh')
        sect2 = Section('blah')
        self.site2.add(sect1, inMenu=True)
        self.site2.add(sect2, inMenu=True)
            
        def lookAtPatterns():
            l = []
            for pattern in self.site.includes():
                l.append(pattern[0])
            return l
        
        def checkLengths(site, info=None, base=None, menu=None):
            if info:
                len(site.info) | should_be | info
            
            if base:
                len(site.base) | should.be | base
            
            if menu:
                [m for m in site.menu()] | should | have(menu).sections
        
        self.checkLengths = checkLengths
        self.lookAtPatterns = lookAtPatterns
    
    describe 'adding sections and sites':
            
        it 'should be possible to add one':
            self.site.add(self.sect1)
            
            self.checkLengths(self.site, info=1, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^some/?$']
            
        it 'should be possible to consecutively add more than one section':            
            self.site.add(self.sect1)
            self.site.add(self.sect2)
            self.site.add(self.sect3)
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^some/?$', '^very/?$', '^nice/?$', '^place/?$']
        
        it 'should be possible to add sections with different include names':            
            self.site.add(self.sect1, includeAs='blah')
            self.site.add(self.sect2)
            self.site.add(self.sect3, includeAs='meh')
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/?$', '^very/?$', '^meh/?$', '^place/?$']
        
        it 'should be possible to add sections to menu when you add them':
            self.checkLengths(self.site, menu=0)       
            
            self.site.add(self.sect1, inMenu=True)
            self.site.add(self.sect2, inMenu=True)
            self.site.add(self.sect3, inMenu=True)
            self.site.add(self.sect4, inMenu=True)
            
            self.checkLengths(self.site, info=4, base=0, menu=4)
            [m for m in self.site.menu()] | should.equal_to | [self.sect1, self.sect2, self.sect3, self.sect4]
        
        it 'should be possible to add a section as a base':           
            self.site.add(self.sect1)
            self.site.add(self.sect2, base=True)
            self.site.add(self.sect3)
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=3, base=1, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^$', '^some/?$', '^nice/?$', '^place/?$']
            
        it 'should be possible to add a site as a base':           
            self.site.add(self.sect1)
            self.site.add(self.site2, base=True)
            self.site.add(self.sect3)
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=3, base=1, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^$', '^some/?$', '^nice/?$', '^place/?$']
        
        it 'should be possible to reorder a section by adding it again':           
            self.site.add(self.sect1, includeAs='blah')
            self.site.add(self.sect2)
            self.site.add(self.sect3, includeAs='meh')
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/?$', '^very/?$', '^meh/?$', '^place/?$']
            
            self.site.add(self.sect2)
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/?$', '^meh/?$', '^place/?$', '^very/?$']
            
            self.site.add(self.sect3, includeAs='meh')
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/?$', '^place/?$', '^very/?$', '^meh/?$']
            
            self.site.add(self.sect3)
            self.checkLengths(self.site, info=5, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/?$', '^place/?$', '^very/?$', '^meh/?$', '^nice/?$']
            
        it 'should be able to import a section from a string':
            self.site.add('urls.tests.fixture.sect1')
            self.checkLengths(self.site, info=1, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^meh/?$']
            
        it 'should be able to add a site from a string':
            self.site.add(site='urls.tests.fixture.theTestSite')
            self.checkLengths(self.site, info=1, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^tester/?$']
        
        it 'should be able to add all menu items from a site when adding it':
            self.checkLengths(self.site2, info=2, menu=2)
            
            self.site.add(site=self.site2, inMenu=True)
            self.checkLengths(self.site, info=1, menu=2)
    
    describe 'merging a site':
        pass
            
            
