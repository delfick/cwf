# coding: spec

from urls.section import Values
        
import fudge
                
def compare(x, y):
    if x > y:
        return -1
    elif x==y:
        return 0
    else: # x<y
        return 1
        
describe 'cwf Values':
    before_each:
        self.request = fudge.Fake("request")
        
    it 'should be able to store values as an iterable':
        v = Values([1,2,3])
        v.getValues(self.request, [], []) | should.equal_to | [(1, 1), (2, 2), (3, 3)]
        
        v = Values(xrange(3))
        v.getValues(self.request, [], []) | should.equal_to | [(0, 0), (1, 1), (2, 2)]
        
    it 'should be able to store values as a callable object return an iterable':
        v = Values(lambda (r, pu, p): [1,2,3], asSet=False)
        v.getValues(self.request, [], []) | should.equal_to | [(1, 1), (2, 2), (3, 3)]
        
        v = Values(lambda (r, pu, p): xrange(3), asSet=False)
        v.getValues(self.request, [], []) | should.equal_to | [(0, 0), (1, 1), (2, 2)]
        
    it 'should pass path into callable used to get values':
        v = Values(lambda (r, pu, p): p, asSet=False)
        v.getValues(self.request, [], ['', 'some', 'path']) | should.equal_to | [('', ''), ('some', 'some'), ('path', 'path')]
        
    it 'should possible to remove duplicates':
        v = Values([1, 1, 2, 3, 4, 2, 2, 3], asSet=True)
        result = v.getValues(self.request, [], []) 
        result | should.include_all_of | [(1, 1), (2, 2), (3, 3), (4, 4)]
        result | should | have(4).elements
        
        v = Values(lambda (r, pu, p): [1, 1, 2, 3, 4, 2, 2, 3], asSet=True)
        result = v.getValues(self.request, [], []) 
        result | should.include_all_of | [(1, 1), (2, 2), (3, 3), (4, 4)]
        result | should | have(4).elements
        
    it 'should be possble to specify a transformation of values':
        v = Values([1, 2, 3], lambda (r, pu, p), v : ('%s_' % v, '__%s' % v), asSet=False)
        v.getValues(self.request, [], []) | should.equal_to | [('1_', '__1'), ('2_', '__2'), ('3_', '__3')]
    
    describe 'sorting values':
        it 'should be possible to specify sorting without a function':
            v = Values([4, 3, 2, 1], sorter=True, asSet=False)
            v.getValues(self.request, [], []) | should.equal_to | [(1, 1), (2, 2), (3, 3), (4, 4)]
            
        it 'should be possible to specify sorting with a function':
            v = Values([1, 2, 3, 4], sorter=compare, asSet=False)
            v.getValues(self.request, [], []) | should.equal_to | [(4, 4), (3, 3), (2, 2), (1, 1)]
        
        it 'should be possible to specify sorting before transformation':
            v = Values([1, 2, 3, 4], lambda (r, pu, p), v : (5-v, v), sorter=True, sortWithAlias=False, asSet=False)
            v.getValues(self.request, [], []) | should.equal_to | [(4, 1), (3, 2), (2, 3), (1, 4)]
            
        it 'should be possible to specify sorting after transformation':
            v = Values([1, 2, 3, 4], lambda (r, pu, p), v : (5-v, v), sorter=True, sortWithAlias=True, asSet=False)
            v.getValues(self.request, [], []) | should.equal_to | [(1, 4), (2, 3), (3, 2), (4, 1)]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
