# coding: spec

from django.http import HttpResponse, Http404
from utils.testing import RequestFactory
from views import View

class View1(View):
    def base(self, state):
        File = 'test.html'
        extra = {'test' : 'view1'}
        return File, extra
    
    def other(self, state):
        return self.redirect(state, '/asdf')
    
    def nothing(self, state):
        return None
    
    def stuff(self, state):
        File = 'test.html'
        extra = {'test' : 'stuff' }
        def modFunc(result):
            return result.replace('b', 'c')
        
        return self.render(state, File, extra, modify=modFunc)
    
    def thing(self, state):
        return self.stuff
    
class View2(View):
    def override(self, state):
        File = 'test.html'
        extra = {'test' : 'override'}
        return File, extra
    
    def base(self, state):
        File = 'test.html'
        extra = {'test' : 'view2'}
        return File, extra
    
describe 'Getting result from a view':
    before_each:
        self.view = View1()
        
        def getResult(view, target):
            client = RequestFactory()
            request = client.get('/')
            return view(request, target, None, None)
        
        self.getResult = getResult
    
    @raises(Http404)
    it 'should raise a 404 if view returns None':
        self.getResult(self.view, 'nothing')
        
    it 'should be possible to get a HttpResponse created from a File_extra tuple':
        result = self.getResult(self.view, 'base')
        result.content | should.equal_to | "<b>view1</b>\n"
    
    it 'should be possible to have class_wide override method':
        result = self.getResult(View2(), 'base')
        result.content | should.equal_to | "<b>override</b>\n"
    
    it 'should be possible to return a HttpResponse object from a view':
        result = self.getResult(self.view, 'other')
        result.status_code | should.equal_to | 302
    
    it 'should be possible to return a callable from a view':
        result = self.getResult(self.view, 'thing')
        result.content | should.equal_to | "<c>stuff</c>\n"
