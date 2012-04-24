# coding: spec

from src.sections.section_master import (
      memoized, memoizer, make_memoizer
    , SectionMaster, Info
    )

import fudge

describe "Memoize logic":
    describe "memoized":
        before_each:
            self.typ = fudge.Fake("typ")
            self.obj = fudge.Fake("obj")
            self.obj_id = fudge.Fake("obj_id")
            
            self.slf = fudge.Fake('slf')
            self.calculator = fudge.Fake("calculator")
            self.slf.calculator = self.calculator
        
        @fudge.patch("__builtin__.id")
        it "gets id of obj and stores result of self.calculator.<typ>_value for that obj for that type", fake_id:
            kwa = fudge.Fake("kwa")
            value = fudge.Fake("value")
            
            fake_id.expects_call().with_args(self.obj).returns(self.obj_id)
            self.slf.results = {self.typ:{}}
            
            self.calculator.expects("%s_value" % self.typ).with_args(self.obj, kw=kwa).returns(value)
            memoized(self.slf, self.typ, self.obj, kw=kwa) |should| be(value)
            self.slf.results |should| equal_to({self.typ:{self.obj_id:value}})
        
        @fudge.patch("__builtin__.id")
        it "returns existing value for id of the object and type if already has it", fake_id:
            kwa = fudge.Fake("kwa")
            value = fudge.Fake("value")
            
            fake_id.expects_call().with_args(self.obj).returns(self.obj_id)
            self.slf.results = {self.typ:{self.obj_id:value}}
            memoized(self.slf, self.typ, self.obj, kw=kwa) |should| be(value)
    
    describe "memoizer":
        before_each:
            self.typ = fudge.Fake("typ")
            self.obj = fudge.Fake("obj")
            self.slf = fudge.Fake('slf')
            self.memoized = fudge.Fake("memoized")
            self.slf.memoized = self.memoized
        
        it "returns a function that calls self.memoized with given type and object":
            kwa = fudge.Fake("kwa")
            value = fudge.Fake("value")
            self.memoized.expects_call().with_args(self.typ, self.obj, kw=kwa).returns(value)
            memoizer(self.typ)(self.slf, self.obj, kw=kwa) |should| be(value)
    
    describe "Making Memoized class":
        before_each:
            self.calculator = fudge.Fake("calculator")
        
        @fudge.test
        it "creates a class with memoized and given calculator on it":
            result = make_memoizer(self.calculator)
            result.memoized.im_func |should| be(memoized)
            result.calculator |should| be(self.calculator)
        
        it "puts properties for each namespace that will call memoized with that namespace and provided arguments":
            kwa1 = fudge.Fake("kwa1")
            kwa2 = fudge.Fake("kwa2")
            obj1 = fudge.Fake("obj1")
            obj2 = fudge.Fake("obj2")
            value1 = fudge.Fake("value1")
            value2 = fudge.Fake("value2")
            
            result = make_memoizer(self.calculator, "one", "two", "three")()
            fake_memoized = (fudge.Fake("memoized").expects_call()
                .with_args("one", obj1, kw1=kwa1).returns(value1)
                .next_call().with_args("three", obj2, kw2=kwa2).returns(value2)
                )
            with fudge.patched_context(result, 'memoized', fake_memoized):
                result.one(obj1, kw1=kwa1) |should| be(value1)
                result.three(obj2, kw2=kwa2) |should| be(value2)

describe "SectionMaster":
    before_each:
        self.request = fudge.Fake("request")
        self.master = SectionMaster(self.request)
    
    describe "initialization":
        it "sets request from what is passed in":
            self.master.request |should| be(self.request)
        
        it "creates a mmoized class that memoizes url_parts, show, exists, display, selected with master as calculator":
            kwa1 = fudge.Fake("kwa1")
            kwa2 = fudge.Fake("kwa2")
            obj1 = fudge.Fake("obj1")
            obj2 = fudge.Fake("obj2")
            fakes = {}
            values = {}
            namespaces = ("url_parts", "show", "exists", "display", "selected")
            
            for namespace in namespaces:
                faked_namespace = fudge.Fake(namespace)
                values[namespace] = {}
                values[namespace][obj1] = fudge.Fake("%s:%s" % (namespace, obj1))
                values[namespace][obj2] = fudge.Fake("%s:%s" % (namespace, obj2))
                (faked_namespace.expects_call()
                    .with_args(obj1, kw=kwa1).returns(values[namespace][obj1])
                    .next_call().with_args(obj2, kw=kwa2).returns(values[namespace][obj2])
                    )
                fakes[namespace] = fudge.patch_object(self.master, "%s_value" % namespace, faked_namespace)
            
            for namespace in namespaces:
                getattr(self.master.memoized, namespace)(obj1, kw=kwa1) |should| be(values[namespace][obj1])
                getattr(self.master.memoized, namespace)(obj1, kw=kwa1) |should| be(values[namespace][obj1])
                
                getattr(self.master.memoized, namespace)(obj2, kw=kwa2) |should| be(values[namespace][obj2])
                getattr(self.master.memoized, namespace)(obj1, kw=kwa1) |should| be(values[namespace][obj1])
                
                getattr(self.master.memoized, namespace)(obj2, kw=kwa2) |should| be(values[namespace][obj2])
                getattr(self.master.memoized, namespace)(obj1, kw=kwa1) |should| be(values[namespace][obj1])
            
            for fake in fakes.values():
                fake.restore()

    describe "Getting Values":
        before_each:
            self.parent = fudge.Fake("parent")
            self.parent2 = fudge.Fake("parent2")
            self.options = fudge.Fake("options")
            
            self.section = fudge.Fake("section")
            self.section2 = fudge.Fake("section2")
            
            self.fake_memoized = fudge.Fake("memoized")
            self.patched = fudge.patch_object(self.master, 'memoized', self.fake_memoized)
        
        after_each:
            self.patched.restore()
        
        describe "getting show, display and exists":
            before_each:
                self.namespaces = ('show', 'display', 'exists')
            
            it "returns False if has parent and parent says no":
                self.fake_memoized.remember_order()
                for namespace in self.namespaces:
                    self.fake_memoized.expects(namespace).with_args(self.parent).returns(False)
                
                self.section.parent = self.parent
                for namespace in self.namespaces:
                    getattr(self.master, "%s_value" % namespace)(self.section) |should| be(False)
            
            it "returns what options says if there is a parent and it says yes":
                self.options.remember_order()
                self.fake_memoized.remember_order()
                result = {}
                for namespace in self.namespaces:
                    result[namespace] = fudge.Fake("%s_value" % namespace)
                    self.fake_memoized.expects(namespace).with_args(self.parent).returns(True)
                    self.options.expects(namespace).with_args(self.request).returns(result[namespace])
                
                self.section.parent = self.parent
                self.section.options = self.options
                for namespace in self.namespaces:
                    getattr(self.master, "%s_value" % namespace)(self.section) |should| be(result[namespace])
                    
            it "returns what options says if there is no parent":
                self.options.remember_order()
                result = {}
                for namespace in self.namespaces:
                    result[namespace] = fudge.Fake("%s_value" % namespace)
                    self.options.expects(namespace).with_args(self.request).returns(result[namespace])
                
                self.section.parent = None
                self.section.options = self.options
                for namespace in self.namespaces:
                    getattr(self.master, "%s_value" % namespace)(self.section) |should| be(result[namespace])
        
        describe "Getting url parts":
            it "if no parent then it returns list of ['', section.url] with no leading slash":
                self.section.url = '/hi'
                self.section.parent = None
                self.master.url_parts_value(self.section) |should| equal_to(['', 'hi'])
                
                self.section2.url = 'hi'
                self.section2.parent = None
                self.master.url_parts_value(self.section2) |should| equal_to(['', 'hi'])
        
            it "prepends section.url with parts from parent if it has one":
                (self.fake_memoized.expects("url_parts")
                    .with_args(self.parent).returns(['', 'one', 'two'])
                    .next_call().with_args(self.parent2).returns(['four'])
                    )
                
                self.section.url = '/hi'
                self.section.parent = self.parent
                self.master.url_parts_value(self.section) |should| equal_to(['', 'one', 'two', 'hi'])
                
                self.section2.url = 'hi'
                self.section2.parent = self.parent2
                self.master.url_parts_value(self.section2) |should| equal_to(['', 'four', 'hi'])
