# coding: spec

from django.views.generic.simple import redirect_to
from urls.section import Options
from urls import dispatch

describe 'cwf Options':
    before_each:
        self.opts = Options(target='view', kls='a', module='m')
        self.opts.nonClonedAttribute = False
    
    it 'should be possible to clone an options object':
        self.opts.nonClonedAttribute | should.be | False
        clone = self.opts.clone()
        clone | should_not | respond_to('nonClonedAttribute')
    
        clone.module | should.equal_to | 'm'
        clone.kls | should.equal_to | 'a'
        
        clone = self.opts.clone(match='z', module='y')
        clone.match | should.equal_to | 'z'
        clone.module | should.equal_to | 'y'
        clone.kls | should.equal_to | 'a'
    
    it 'should reset alias and match and values when cloning unless specified':
        self.opts.update(values='blah', match='meh', alias='hello')
        
        clone = self.opts.clone()
        clone.alias | should.equal_to | None
        clone.match | should.equal_to | None
        clone.values | should.equal_to | None
        
        clone = self.opts.clone(carryAll=True)
        clone.alias | should.equal_to | 'hello'
        clone.match | should.equal_to | 'meh'
        clone.values | should.equal_to | 'blah'
        
    
    it 'should have a function saying whether there is a condition to section being viewed':
        self.opts.condition = True
        self.opts.show() | should.be | False
        
        self.opts.condition = lambda : True
        self.opts.show() | should.be | False
        
        self.opts.condition = lambda : False
        self.opts.show() | should.be | True
        
        self.opts.condition = False
        self.opts.show() | should.be | True
        
        self.opts.condition = None
        self.opts.show() | should.be | True
        
    describe 'getting object':
        before_each:
            self.opts = Options(module="urls.dispatch", kls="dispatch")
            
        it 'should consider a non string object for kls as good enough':
            o = self.opts.clone(kls=dispatch)
            o.getObj() | should.be | dispatch
        
        it 'should return attribute of module if module nonstring and kls is a string with no dots inside':
            o = self.opts.clone(module=dispatch, kls='dispatch')
            o.getObj() | should.be | getattr(dispatch, 'dispatch')
            
            o = self.opts.clone(module=dispatch, kls='dispatch.')
            o.getObj() | should.be | getattr(dispatch, 'dispatch')
            
            o = self.opts.clone(module=dispatch, kls='.dispatch')
            o.getObj() | should.be | getattr(dispatch, 'dispatch')
            
            o = self.opts.clone(module=dispatch, kls='.dispatch.')
            o.getObj() | should.be | getattr(dispatch, 'dispatch')
    
        it 'should follow the dots if module is nonstring and kls is a string with dots inside':
            o = self.opts.clone(module=dispatch, kls='dispatch.__call__')
            o.getObj() | should.equal_to | dispatch.dispatch.__call__
    
        it 'should return a string if both module and kls are strings':
            o = self.opts.clone(module='dispatch', kls='dispatch.__call__')
            o.getObj() | should.equal_to | 'dispatch.dispatch.__call__'
    
    describe 'getting url pattern':
        before_each:
            self.opts = Options(target='t')
                
        it 'should return a tuple with four items':
            for thing in self.opts.urlPattern(''):
                thing | should | have(4).parts
    
        describe '___the pattern':
            before_each:
                def pattern(*patterns):
                    for pat in patterns:
                        for thing in self.opts.urlPattern(pat):
                            yield thing[0]
                
                self.pattern = pattern
                
            it 'should have no double slashes in it':
                            
                for pat in self.pattern(
                    '', '/some_place/nice/', '//some_place/nice/', 
                    '//some_place///nice/', 'some_place/nice/', 
                    'some_place', 'some_place/nice'):
                    pat | should_not.contain | '//'
            
            it 'should add optional slash at end of regex only if pattern doesnt have ending slash':
                for pat in self.pattern(
                    '', '/some_place/nice', '//some_place/nice', '//some_place//nice', '/some_place', 'some_place'
                ):
                    pat | should.end_with | '/*$'
            
            it 'should add optional slash at end of regex only if pattern doesnt have ending slash':
                for pat in self.pattern(
                    '/some_place/nice/', '//some_place/nice/', 
                    '//some_place//nice/', '/some_place/', 'some_place/'
                ):
                    pat | should_not.end_with | '/*$'
                    pat | should.end_with | '/$'
            
            it 'should remove the slash if pattern is just a slash':
                for pat in self.pattern('/'):
                    pat | should.equal_to | '^$'
        
        describe '___the view':
            before_each:
                self.opts = self.opts.clone(module='m', kls='k', target='t')
                
                def redirect(*redirects):
                    for redirect in redirects:
                        o = self.opts.clone(redirect=redirect)
                        for thing in o.urlPattern(''):
                            yield thing[1]
                
                self.redirect = redirect
                
            it 'should ignore target only if redirect is a string or callable returning a string':
                for redirect in self.redirect('/some_place/nice', lambda : '/some_place/nice'):
                    redirect.__name__ | should.be | 'redirector'
                
                for redirect in self.redirect(
                    False, True,
                    lambda : False, lambda : True,
                    1, lambda : 1
                ):
                    redirect | should_not.be | redirect_to
            
            it 'should use bypass dispatcher if target is not a method':
                def aFunction(): pass
                o = self.opts.clone(target=aFunction)
                for thing in o.urlPattern(''):
                    thing[1] | should.be | aFunction
                
            it 'should not bypass dispatcher if target is a method':
                class test(object):
                    def aMethod(self): pass
                    
                o = self.opts.clone(target=test.aMethod)
                for thing in o.urlPattern(''):
                    thing[1] | should.be | dispatch.dispatch
                    
                o = self.opts.clone(target=test().aMethod)
                for thing in o.urlPattern(''):
                    thing[1] | should.be | dispatch.dispatch
        
        describe '___the kwargs':
            
            it 'should have a callable called condition':
                for thing in self.opts.urlPattern(''):
                    callable(thing[2]['condition']) | should.be | True
            
            it 'should have key value pairs from extraContext':
                o = self.opts.clone(extraContext={'hello' : 'there'})
                for thing in self.opts.urlPattern(''):
                    thing[2] | should_not.contain | 'hello'
                    
                for thing in o.urlPattern(''):
                    thing[2] | should.contain | 'hello'
                    thing[2]['hello'] | should.equal_to | 'there'
            
            it 'should have key value pairs overrided from extraContext':
                o = self.opts.clone(extraContext={'target' : 'somewhere_else'})
                
                for thing in self.opts.urlPattern(''):
                    thing[2]['target'] | should.equal_to | 't'
                    
                for thing in o.urlPattern(''):
                    thing[2]['target'] | should.equal_to | 'somewhere_else'
            
            
            
            
            
            
            
            
            
            
            
    
    
    
