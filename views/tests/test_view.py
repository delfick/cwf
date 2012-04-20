# coding: spec

from django.test import TestCase, RequestFactory
from django.http import Http404

from views import DictObj, View
from types  import MethodType

describe 'DictObj':
    before_each:
        self.d = DictObj( a = 5 )
        
    it 'should be possible to access attributes using dictionary syntax':
        self.d['a'] | should.be | 5
        
    it 'should be possible to access attributes using dot syntax':
        self.d.a | should.be | 5
        
    it 'should be possible to set attributes using dot syntax':
        self.d.b = 6
        self.d['b'] | should.be | 6
        self.d.b | should.be | 6
        
    it 'should be possible to set attributes using dictionary syntax':
        self.d['c'] = 7
        self.d['c'] | should.be | 7
        self.d.c | should.be | 7
    
    it 'should be possible to see if it has a particular attribute':
        ('a' in self.d) | should.be | True
        ('b' in self.d) | should.be | False
    
    it 'should be possible to get a list of keys in the dictobj':
        self.d.keys() | should.equal_to | ['a']
        
        self.d.stuff = 'asdf'
        self.d.keys() | should.equal_to | ['a', 'stuff']
    
    it 'should be possible to get a list of values in the dictobj':
        self.d.values() | should.equal_to | [5]
        
        self.d.stuff = 'asdf'
        self.d.values() | should.equal_to | [5, 'asdf']
    
    it 'should be possible to get a list of items in the dictobj':
        self.d.items() | should.equal_to | [('a', 5)]
        
        self.d.stuff = 'asdf'
        self.d.items() | should.equal_to | [('a', 5), ('stuff', 'asdf')]
        
describe TestCase, 'View':
    urls = 'templates.urls'
    before_each:
        self.view = View()
        self.client = RequestFactory()
        self.request1 = self.client.get('/some/path/', {'this': '3', 'that': 5, 'thisthat' : 6})
        self.request2 = self.client.get('/some/other/path/', {'this': '3'})
        self.request3 = self.client.get('/some/other/path/', {'this': '', 'that' : ''})
        self.state = DictObj( baseUrl = '/cwf' )
        
        self.request1.state = self.state
        self.request2.state = self.state
        self.request3.state = self.state
    
    @raises(Http404)
    it 'should be able to raise a 404':
        self.view.raise404()
        
    it 'should have a method that returns a HttpResponse object':
        self.view.http | should.be_kind_of | MethodType
        
    it 'should have a method that simplifies rendering xml':
        self.view.xml | should.be_kind_of | MethodType
        
    it 'should have a method that simplifies creating a redirect':
        self.view.redirect | should.be_kind_of | MethodType
        
    it 'should have a method that simplifies rendering content with a particular mime type':
        self.view.render | should.be_kind_of | MethodType
    
    it 'should have methods to get changelist and addview and changeview for a model in admin':
        self.view.getAdminChangeView | should.be_kind_of | MethodType
        self.view.getAdminAddView | should.be_kind_of | MethodType
        self.view.getAdminChangeList | should.be_kind_of | MethodType
    
    describe 'getGETString':
        before_each:
            
            def use(num, *args, **kwargs):
                func = getattr(self.view, 'getGETString')
                req = getattr(self, 'request%d' % num)
                return func(req, *args, **kwargs)
            
            self.use = use
            
        it 'should be possible to get GET arguements from a request object':
            self.use(1) | should.equal_to | 'this=3;that=5;thisthat=6'
            self.use(2) | should.equal_to | 'this=3'
            self.use(3) | should.equal_to | 'this;that'
            
        it 'should be possible to ignore particular GET arguements':
            self.use(1, ignoreGET=['this']) | should.equal_to | 'that=5;thisthat=6'
            self.use(1, ignoreGET='this') | should.equal_to | 'that=5;thisthat=6'
            self.use(1, ignoreGET='that') | should.equal_to | 'this=3;thisthat=6'
            
            self.use(2, ignoreGET=['this']) | should.equal_to | ''
    
    describe 'redirect':
        before_each:
            
            def use(num, *args, **kwargs):
                func = getattr(self.view, '_redirect')
                request = getattr(self, 'request%d' % num)
                return func(request, *args, **kwargs)
            
            self.use = use
            
        it 'should prepend baseUrl if an absolute path':
            self.use(1, '/somewhere/nice', relative=False) | should.equal_to | '/cwf/somewhere/nice'
            self.use(1, '/somewhere/nice', relative=True)  | should.equal_to | '/cwf/somewhere/nice'
        
        it "should prepend request's path if a relative path":
            self.use(1, 'somewhere/nice', relative=True)   | should.equal_to | '/some/path/somewhere/nice'
            self.use(1, 'somewhere/nice', relative=False)  | should.equal_to | 'somewhere/nice'
            
            self.use(2, 'somewhere/nice', relative=True)   | should.equal_to | '/some/other/path/somewhere/nice'
        
        it "should be able to carry GET parameters":
            self.use(1, 'somewhere', relative=False, carryGET=True) | should.equal_to | 'somewhere?this=3;that=5;thisthat=6'
            self.use(2, 'somewhere', relative=False, carryGET=True) | should.equal_to | 'somewhere?this=3'
