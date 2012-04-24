# coding: spec

from src.sections.dispatch import Dispatcher, dispatcher

from django.http import Http404
import fudge

describe "dispatcher":
    it "is an instance of Dispatcher":
        type(dispatcher) |should| be(Dispatcher)

describe "Dispatcher":
    describe "Getting view":
        before_each:
            self.view = fudge.Fake("view")
            self.location = fudge.Fake("location")
            self.fake_find_view = fudge.Fake("find_view")
            self.dispatcher = type("Dispatcher", (Dispatcher, ), {'find_view' : self.fake_find_view})()
        
        @fudge.test
        it "finds the view for given location if doesn't already have view":
            self.fake_find_view.expects_call().with_args(self.location).returns(self.view)
            self.dispatcher.views |should| be_empty
            self.dispatcher.get_view(self.location) |should| be(self.view)
            self.dispatcher.views |should| equal_to({self.location:self.view})
        
        @fudge.test
        it "returns the view for the provided location":
            self.dispatcher.views[self.location] = self.view
            self.dispatcher.get_view(self.location) |should| be(self.view)

    describe "Finding a view":
        before_each:
            self.dispatcher = Dispatcher()
        
        it "returns location if not a string":
            for location in (fudge.Fake("location"), lambda: 1):
                self.dispatcher.find_view(location) |should| be(location)
        
        @fudge.patch("__builtin__.locals", "__builtin__.globals", "__builtin__.__import__")
        it "using __import__ to find the view if location is a string", fake_locals, fake_globals, fake_import:
            lcls = fudge.Fake("locals")
            glbls = fudge.Fake("globals")
            result = fudge.Fake("result")
            module = fudge.Fake("module")
            module.name = result
            fake_locals.expects_call().returns(lcls)
            fake_globals.expects_call().returns(glbls)
            fake_import.expects_call().with_args("path.to.place", glbls, lcls, ['name'], -1).returns(module)
            
            self.dispatcher.find_view("path.to.place.name") |should| be(result)
    
    describe "Calling the dispatcher":
        before_each:
            self.kls = fudge.Fake("kls")
            self.view = fudge.Fake("view")
            self.target = fudge.Fake("target")
            self.result = fudge.Fake("result")
            self.request = fudge.Fake("request")
            self.section = fudge.Fake("section")
            self.dispatcher = Dispatcher()
        
        @fudge.test
        it "raises Http404 if no section is provided in kwargs":
            caller = lambda: self.dispatcher(self.request, self.kls, self.target)
            Http404 |should| be_thrown_by(caller)
        
        @fudge.test
        it "raises Http404 if section is provided but not reachable for the request":
            self.section.expects("reachable").with_args(self.request).returns(False)
            caller = lambda: self.dispatcher(self.request, self.kls, self.target, section=self.section)
            Http404 |should| be_thrown_by(caller)
        
        @fudge.test
        it "calls view for provided kls with request, target and other arguments if section and section is reachable":
            arg1 = fudge.Fake("arg1")
            arg2 = fudge.Fake("arg2")
            kwa1 = fudge.Fake("kwa1")
            kwa2 = fudge.Fake("kwa2")
            self.section.expects("reachable").with_args(self.request).returns(True)
            self.view.expects_call().with_args(
                self.request, self.target, arg1, arg2, kw1=kwa1, kw2=kwa2, section=self.section
            ).returns(self.result)
            
            fake_get_view = fudge.Fake("get_view").expects_call().with_args(self.kls).returns(self.view)
            with fudge.patched_context(self.dispatcher, 'get_view', fake_get_view):
                self.dispatcher(
                    self.request, self.kls, self.target, arg1, arg2, kw1=kwa1, kw2=kwa2, section=self.section
                ) |should| be(self.result)
