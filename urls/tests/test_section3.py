# coding: spec

from urls.section import Section, Options, Values
import fudge

describe 'Sections':
    before_each:
        self.sect = Section()
        self.request = fudge.Fake("request")
        self.request.user = fudge.Fake("user")
    
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
        
        self.sect.show(self.request) | should.be | True
        c1.show(self.request) | should.be | True
        c2.show(self.request) | should.be | True
        c3.show(self.request) | should.be | False
        
        self.sect.base(condition = True)
        self.sect.show(self.request) | should.be | False
        c1.show(self.request) | should.be | False
        c2.show(self.request) | should.be | False
        c3.show(self.request) | should.be | False
    
    it 'should only be appearable if its showable and displayable':
        self.sect.show(self.request) | should.be | True
        self.sect.options.display | should.be | True
        self.sect.appear(self.request) | should.be | True
        
        self.sect.base(condition = True)
        self.sect.show(self.request) | should.be | False
        self.sect.options.display | should.be | True
        self.sect.appear(self.request) | should.be | False
        
        self.sect.base(condition = False, display=False)
        self.sect.show(self.request) | should.be | True
        self.sect.options.display | should.be | False
        self.sect.appear(self.request) | should.be | False
    
    it 'should be selected if parent is selected and url equals first part of path':
        c = self.sect.add('nice')
        c.determineSelection(['nice', 'place'], True)  | should.equal_to | (True, ['place'])
        c.determineSelection(['nice', 'place'], False) | should.equal_to | (False, [])
        c.determineSelection(['some', 'place'], True)  | should.equal_to | (False, [])
    
    it 'should be possible to adopt a section':
        sect1 = Section('hello')
        sect2 = Section('there')
        
        sect1.adopt(sect2)
        sect2.rootAncestor() | should.be | sect1
        sect1.children | should.equal_to | [sect2]
    
    it 'should be possible to adopt many sections at once':
        sect1 = Section('hello')
        sect2 = Section('there')
        sect3 = Section('blah')
        sect4 = Section('meh')
        
        sect1.adopt(sect2)
        sect2.rootAncestor() | should.be | sect1
        sect1.children | should.equal_to | [sect2]
        
        sect1.adopt(sect3, sect4)
        for sect in (sect3, sect4):
            sect.rootAncestor() | should.be | sect1
        
        sect1.children | should.equal_to | [sect2, sect3, sect4]
    
    describe 'getting alias':
        it 'should be possible to get the alias':
            self.sect.getAlias() | should.equal_to | '/'
            self.sect.options.alias = 'blah'
            self.sect.getAlias() | should.equal_to | 'blah'
        
        it 'should default to the capitalised url':
            self.sect.getAlias() | should.equal_to | '/'
            self.sect.url = 'blah'
            self.sect.getAlias() | should.equal_to | 'Blah'
        
    describe 'info':
        before_each:

            def gen(request, children, restOfPath, parentUrl, parentSelected):
                for child in children:
                    for part in child.getInfo(request, restOfPath, parentUrl, parentSelected, gen=gen):
                        yield part
                        
            def goThrough(gen, *expected):
                result = []
                if gen:
                    if callable(gen):
                        gen = gen()
                    result = [t for t in gen]
                    
                len(expected) | should.equal_to | len(result)
                gens = []
                for i in range(len(result)):
                    next = expected[i]
                    if len(next) == 6:
                        fourth = next[4]
                        fifth = next[5]
                    else:
                        fourth = result[i][5]
                        fifth = next[4]
                    
                    result[i] | should.equal_to | (
                        next[0], result[i][1], next[1], next[2], next[3], fourth, fifth
                    )
                    gens.append(fourth)
                
                return gens
                        
            self.gen = gen
            self.goThrough = goThrough
        
        it 'should not provide a children generator if there are no children':
            c = self.sect.add('there')
            
            gens = self.goThrough(self.sect.getInfo(self.request, [], gen=self.gen), (self.sect, [''], '/', False, self.sect.options))
            gens = self.goThrough(gens[0], (c, ['', 'there'], 'There', False, [], c.options))
            
        it 'should only have info if it is active':
            def test(**kwargs):
                self.sect.base(**kwargs)
                return [t for t in self.sect.getInfo(self.request, [''])]
            
            test() | should | have(1).element
            test(active=False) | should | have(0).elements
            test(exists=False, active=True) | should | have(1).elements
            test(exists=True, active=True, condition=True) | should | have(1).elements
        
        it 'should return a 7 element tuple':
            for t in self.sect.getInfo(self.request, ['']):
                t | should | have(7).elements
            
            self.sect.base(values = Values(['blah'], asSet=False))
            for t in self.sect.getInfo(self.request, ['']):
                t | should | have(7).elements
        
        it 'should use options alias or capitalized url if alias doesnt exist':
            c = self.sect.add('place')
            for t in c.getInfo(self.request, ['']):
                t[3] | should.equal_to | 'Place'
            
            c.base(alias='nice')
            for t in c.getInfo(self.request, ['']):
                t[3] | should.equal_to | 'nice'
        
        it 'should not change alias from a values object':
            self.sect.base(values = Values(['v1', 'v2'], asSet=False))
            [t[3] for t in self.sect.getInfo(self.request, [''])] | should.equal_to | ['v1', 'v2']
        
        it 'should get fullUrl correct':
            for t in self.sect.getInfo(self.request, ['']):
                t[0] | should.equal_to | self.sect
                t[2] | should.equal_to | ['']
            
            c = self.sect.add('some')
            c2 = self.sect.add('meh').base(alias='niceAlias')
            d = c.add('nice').base(match='blah')
            
            gens = self.goThrough(self.sect.getInfo(self.request, [], gen=self.gen), (self.sect, [''], '/', False, self.sect.options))
            
            gens = self.goThrough(gens[0]
                , (c, ['', 'some'], 'Some', False, c.options)
                , (c2, ['', 'meh'], 'niceAlias', False, [], c2.options)
            )
            
            self.goThrough(gens[1])
            self.goThrough(gens[0], (d, ['', 'some', 'nice'], 'Nice', False, d.options))

        it 'should get fullUrl correct when there are dynamic values concerned':
            c = self.sect.add('some').base(values=Values(['v1', 'v2'], asSet=False))
            d = c.add('nice')
            
            gens = self.goThrough(self.sect.getInfo(self.request, [], gen=self.gen), (self.sect, [''], '/', False, self.sect.options))
        
            gens = self.goThrough(gens[0]
                , (c, ['', 'v1'], 'v1', False, c.options)
                , (c, ['', 'v2'], 'v2', False, c.options)
            )
            
            self.goThrough(gens[0], (d, ['', 'v1', 'nice'], 'Nice', False, [], d.options))
            self.goThrough(gens[1], (d, ['', 'v2', 'nice'], 'Nice', False, [], d.options))
        
        it 'should be able to determine if selected correctly':
            c = self.sect.add('some').base(alias='asdf')
            d = self.sect.add('every')
            e = c.add('nice')
            f = e.add('place')
            g = d.add('bad_place')
            
            gens = self.goThrough(
                  self.sect.getInfo(self.request, ['', 'some', 'nice', 'country'], gen=self.gen)
                , (self.sect, [''], '/', True, self.sect.options)
            )
        
            gens = self.goThrough(gens[0]
                , (c, ['', 'some'], 'asdf', True, c.options)
                , (d, ['', 'every'], 'Every', False, d.options)
            )
            
            self.goThrough(gens[1], (g, ['', 'every', 'bad_place'], 'Bad_place', False, [], g.options))
            gens = self.goThrough(gens[0], (e, ['', 'some', 'nice'], 'Nice', True, e.options))
            
            self.goThrough(gens[0], (f, ['', 'some', 'nice', 'place'], 'Place', False, [], f.options))
        
        it 'should determine if selected correctly when a section has showbase equal to False':
            c = self.sect.add('some').base(alias='asdf', showBase=False)
            d = self.sect.add('every')
            e = c.add('nice').base(showBase=False)
            f = e.add('place')
            g = d.add('bad_place')
            
            gens = self.goThrough(
                  self.sect.getInfo(self.request, ['', 'some', 'nice', 'country'], gen=self.gen)
                , (self.sect, [''], '/', True, self.sect.options)
            )
        
            gens = self.goThrough(gens[0]
                , (c, ['', 'some'], 'asdf', True, c.options)
                , (d, ['', 'every'], 'Every', False, d.options)
            )
            
            self.goThrough(gens[1], (g, ['', 'every', 'bad_place'], 'Bad_place', False, [], g.options))
            gens = self.goThrough(gens[0], (e, ['', 'some', 'nice'], 'Nice', True, e.options))
            
            self.goThrough(gens[0], (f, ['', 'some', 'nice', 'place'], 'Place', False, [], f.options))
        
        it 'should determine if selected correctly when there are dynamic values concerned':
            c = self.sect.add('some').base(showBase=False, values=Values(['some', 'blah'], asSet=False))
            d = self.sect.add('every')
            e = c.add('nice').base(showBase=False)
            f = e.add('place')
            g = d.add('bad_place')
            
            gens = self.goThrough(
                  self.sect.getInfo(self.request, ['', 'some', 'nice', 'country'], gen=self.gen)
                , (self.sect, [''], '/', True, self.sect.options)
            )
        
            gens = self.goThrough(gens[0]
                , (c, ['', 'some'], 'some', True, c.options)
                , (c, ['', 'blah'], 'blah', False, c.options)
                , (d, ['', 'every'], 'Every', False, d.options)
            )
            
            self.goThrough(gens[2], (g, ['', 'every', 'bad_place'], 'Bad_place', False, [], g.options))
            
            gens1 = self.goThrough(gens[1], (e, ['', 'blah', 'nice'], 'Nice', False, e.options))
            gens2 = self.goThrough(gens[0], (e, ['', 'some', 'nice'], 'Nice', True, e.options))
            
            self.goThrough(gens1[0], (f, ['', 'blah', 'nice', 'place'], 'Place', False, [], f.options))
            self.goThrough(gens2[0], (f, ['', 'some', 'nice', 'place'], 'Place', False, [], f.options))
        
    describe 'options':
        it 'should always have an options object':
            self.sect.options | should.be_kind_of | Options
        
        it 'should extend the sections options object upon calling base':
            self.sect.options.target = 'base'
            
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
    
    describe 'urlPatterns':
        it 'should not break when calling patterns':
            self.sect.patterns | should_not | throw(Exception)
            
        it 'should not break when calling patternList':
            self.sect.patternList | should_not | throw(Exception)
            
        it 'should not break when calling urlPattern':
            self.sect.urlPattern | should_not | throw(Exception)
        
        it 'should not break when calling patterns when we have children':
            s = self.sect.add('some')
            n = self.sect.add('nice')
            p = self.sect.add('place')
            self.sect.patterns | should_not | throw(Exception)
            
            f = self.sect.first('first')
            self.sect.patterns | should_not | throw(Exception)
            
            s.add('c1')
            s.first('cf')
            p.add('c2')
            f.first('blah')
            f.add('asdf')
            self.sect.patterns | should_not | throw(Exception)
        
        it 'should not break when calling patternList when we have children':
            s = self.sect.add('some')
            n = self.sect.add('nice')
            p = self.sect.add('place')
            self.sect.patternList | should_not | throw(Exception)
            
            f = self.sect.first('first')
            self.sect.patternList | should_not | throw(Exception)
            
            s.add('c1')
            s.first('cf')
            p.add('c2')
            f.first('blah')
            f.add('asdf')
            self.sect.patternList | should_not | throw(Exception)
            
        describe '___getting pattern':
            it 'it already has underscore pattern variable it should return that':
                self.sect._pattern = 'asdf'
                self.sect.getPattern() | should.equal_to | 'asdf'
            
            it 'should just return url if no parent or match':
                self.sect.getPattern() | should.equal_to | ['/']
            
            it 'should return regex named group if has match':
                self.sect.base(match='place')
                self.sect.getPattern() | should.equal_to | ['(?P<place>/)']
            
            it 'should use parent patterns':
                c = self.sect.add('some')
                d = c.add('place').base(match="nice")
                
                d.getPattern() | should.equal_to | ['/', 'some', '(?P<nice>place)']
        
            it 'should stop adding patterns when hitting specified section':
                c = self.sect.add('some')
                d = c.add('nice')
                e = d.add('place')
                
                e.getPattern(c) | should.equal_to | ['some', 'nice', 'place']
