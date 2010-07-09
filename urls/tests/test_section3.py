# coding: spec

from urls.section import Section, Options

describe 'Sections':
    before_each:
        self.sect = Section()
    
    it 'should implement __iter__ and return itself followed by children':
        def result():
            return [t for t in self.sect]
        
        result() | should.equal_to | [self.sect]
        
        f = self.sect.first()
        result() | should.equal_to | [self.sect, f]
        
        next1 = self.sect.add('some')
        next2 = self.sect.add('place')
        next3 = self.sect.add('nice')
        
        result() | should.equal_to | [self.sect, f, next1, next2, next3]
        
        f2 = self.sect.first()
        result() | should.equal_to | [self.sect, f2, next1, next2, next3]
    
    it 'should be possible to determine root ancestor':
        c1 = self.sect.add('some')
        c2 = self.sect.add('place')
        c3 = self.sect.add('not_nice')
        
        c3.rootAncestor() | should.be | self.sect
    
    it 'should only be showable if its options says so and its parent is':
        c1 = self.sect.add('some')
        c2 = self.sect.add('place')
        c3 = self.sect.add('not_nice').base(condition=True)
        
        self.sect.show() | should.be | True
        c1.show() | should.be | True
        c2.show() | should.be | True
        c3.show() | should.be | False
        
        self.sect.base(condition = True)
        self.sect.show() | should.be | False
        c1.show() | should.be | False
        c2.show() | should.be | False
        c3.show() | should.be | False
    
    it 'should only be appearable if its showable and displayable':
        self.sect.show() | should.be | True
        self.sect.options.display | should.be | True
        self.sect.appear() | should.be | True
        
        self.sect.base(condition = True)
        self.sect.show() | should.be | False
        self.sect.options.display | should.be | True
        self.sect.appear() | should.be | False
        
        self.sect.base(condition = False, display=False)
        self.sect.show() | should.be | True
        self.sect.options.display | should.be | False
        self.sect.appear() | should.be | False
    
    it 'should be selected if parent is selected and url equals first part of path':
        c = self.sect.add('nice')
        c.determineSelection(['nice', 'place'], True)  | should.equal_to | (True, ['place'])
        c.determineSelection(['nice', 'place'], False) | should.equal_to | (False, [])
        c.determineSelection(['some', 'place'], True)  | should.equal_to | (False, [])
    
    describe 'info':
        it 'should only have info if exists and is active and is allowed to be shown':
            def test(**kwargs):
                self.sect.base(**kwargs)
                return [t for t in self.sect.getInfo([''])]
            
            test() | should | have(1).element
            test(exists=False) | should | have(0).elements
            test(exists=True, active=False) | should | have(0).elements
            test(exists=True, active=True, condition=True) | should | have(0).elements
        
        it 'should have more tests'
        
    describe 'options':
        it 'should always have an options object':
            self.sect.options | should.be_kind_of | Options
        
        it 'should extend the sections options object upon calling base':
            self.sect.options.target | should.equal_to | 'base'
            
            self.sect.base(target='t')
            self.sect.options.target | should.equal_to | 't'
        
        it 'should return the section when calling base':
            self.sect.base() | should.be | self.sect
    
    describe 'children':
        it 'should complain if we try to add a section with url as an empty string':
            (self.sect.add, '') | should | throw(ValueError)
        
        it 'should have a method letting us add a section with an empty url':
            f = self.sect.first()
            self.sect.children[0] | should.be | f
            f.url | should.equal_to | ''
            
            sect2 = Section()
            sect2.add('some')
            sect2.add('place')
            sect2.add('nice')
            
            f = sect2.first()
            sect2.children[0] | should.be | f
            f.url | should.equal_to | ''
        
        it 'should only be able to have one first child':
            self.sect.first()
            self.sect.first()
            
            self.sect.children | should | have(1).child
        
        it 'should return child from calling add and first':
            child = self.sect.add('some')
            child | should.be_kind_of | Section
            child | should_not.be | self.sect
            
            child = self.sect.first()
            child | should.be_kind_of | Section
            child | should_not.be | self.sect
        
        it 'should pass on a clone of the sections options when adding children':
            sect = Section().base(target = 't')
            
            child = sect.add('some')
            child.options | should_not.be | self.sect.options
            child.options.target | should.equal_to | 't'
            
            sect.base(target = 'd')
            child = sect.first()
            child.options | should_not.be | self.sect.options
            child.options.target | should.equal_to | 'd'
        
        it 'should give children a parent equal to that section':
            self.sect.add('hello').parent | should.be | self.sect
            self.sect.first().parent | should.be | self.sect
        
