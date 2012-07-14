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
        
        it "can take in None as a value":
            value = fudge.Fake("value")
            self.slf.results = {self.typ:{}}
            self.calculator.expects("%s_value" % self.typ).with_args(None).returns(value).times_called(1)
            memoized(self.slf, self.typ, None) |should| be(value)
            memoized(self.slf, self.typ, None) |should| be(value)
    
    describe "memoizer":
        before_each:
            self.typ = fudge.Fake("typ")
            self.obj = fudge.Fake("obj")
            self.slf = fudge.Fake('slf')
            self.memoized = fudge.Fake("memoized")
            self.slf.memoized = self.memoized
        
        @fudge.test
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
        
        @fudge.test
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
        
        @fudge.test
        it "creates a memoized class that memoizes url_parts, active, exists, display, selected with master as calculator":
            kwa1 = fudge.Fake("kwa1")
            kwa2 = fudge.Fake("kwa2")
            obj1 = fudge.Fake("obj1")
            obj2 = fudge.Fake("obj2")
            fakes = {}
            values = {}
            namespaces = ("url_parts", "active", "exists", "display", "selected")
            
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
        
        describe "getting active and exists":
            before_each:
                self.namespaces = ('active', 'exists')
            
            @fudge.test
            it "returns False if has parent and parent says no":
                self.fake_memoized.remember_order()
                for namespace in self.namespaces:
                    self.fake_memoized.expects(namespace).with_args(self.parent).returns(False)
                
                self.section.parent = self.parent
                for namespace in self.namespaces:
                    getattr(self.master, "%s_value" % namespace)(self.section) |should| be(False)
            
            @fudge.test
            it "returns what options says if there is a parent and it says yes":
                self.options.remember_order()
                self.fake_memoized.remember_order()
                result = {}
                for namespace in self.namespaces:
                    result[namespace] = fudge.Fake("%s_value" % namespace)
                    self.fake_memoized.expects(namespace).with_args(self.parent).returns(True)
                    self.options.expects('conditional').with_args(namespace, self.request).returns(result[namespace])
                
                self.section.parent = self.parent
                self.section.options = self.options
                for namespace in self.namespaces:
                    getattr(self.master, "%s_value" % namespace)(self.section) |should| be(result[namespace])
                    
            @fudge.test
            it "returns what options says if there is no parent":
                self.options.remember_order()
                result = {}
                for namespace in self.namespaces:
                    result[namespace] = fudge.Fake("%s_value" % namespace)
                    self.options.expects('conditional').with_args(namespace, self.request).returns(result[namespace])
                
                self.section.parent = None
                self.section.options = self.options
                for namespace in self.namespaces:
                    getattr(self.master, "%s_value" % namespace)(self.section) |should| be(result[namespace])
        
        describe "Getting display":
            @fudge.test
            it "Returns False, True if parent has False, True":
                self.section.parent = self.parent
                self.fake_memoized.expects('display').with_args(self.parent).returns((False, True))
                self.master.display_value(self.section) |should| equal_to((False, True))

            @fudge.test
            it "returns section.can_display if no parent":
                result = fudge.Fake("result")
                self.section.expects("can_display").with_args(self.request).returns(result)
                self.master.display_value(self.section) |should| be(result)

            @fudge.test
            it "returns section.can_display if parent can be displayed":
                result = fudge.Fake("result")
                self.section.parent = self.parent

                self.fake_memoized.expects('display').with_args(self.parent).returns((True, True))
                self.section.expects("can_display").with_args(self.request).returns(result)

                self.master.display_value(self.section) |should| be(result)

            @fudge.test
            it "returns section.can_display if parent can't be displayed but it says to not propogate display":
                result = fudge.Fake("result")
                self.section.parent = self.parent

                self.fake_memoized.expects('display').with_args(self.parent).returns((False, False))
                self.section.expects("can_display").with_args(self.request).returns(result)

                self.master.display_value(self.section) |should| be(result)

        describe "Getting url parts":
            before_each:
                self.section.options = fudge.Fake("options")
                self.section2.options = fudge.Fake("options2")

            it "returns empty list if given None":
                self.master.url_parts_value(None) |should| equal_to([])
            
            @fudge.test
            it "if no parent then it returns list of ['', section.url] with no leading slash":
                self.section.url = '/hi'
                self.section.parent = None
                self.section.options.has_attr(promote_children=False)
                self.master.url_parts_value(self.section) |should| equal_to(['', 'hi'])
                
                self.section2.url = 'hi'
                self.section2.parent = None
                self.section2.options.has_attr(promote_children=False)
                self.master.url_parts_value(self.section2) |should| equal_to(['', 'hi'])

            @fudge.test
            it "if no parent and promotes children then it returns list of [''] with no leading slash":
                self.section.url = '/hi'
                self.section.parent = None
                self.section.options.has_attr(promote_children=True)
                self.master.url_parts_value(self.section) |should| equal_to([''])
                
                self.section2.url = 'hi'
                self.section2.parent = None
                self.section2.options.has_attr(promote_children=True)
                self.master.url_parts_value(self.section2) |should| equal_to([''])
        
            @fudge.test
            it "prepends section.url with parts from parent if it has one":
                (self.fake_memoized.expects("url_parts")
                    .with_args(self.parent).returns(['', 'one', 'two'])
                    .next_call().with_args(self.parent2).returns(['four'])
                    )
                
                self.section.url = '/hi'
                self.section.parent = self.parent
                self.section.options.has_attr(promote_children=False)
                self.master.url_parts_value(self.section) |should| equal_to(['', 'one', 'two', 'hi'])
                
                self.section2.url = 'hi'
                self.section2.parent = self.parent2
                self.section2.options.has_attr(promote_children=False)
                self.master.url_parts_value(self.section2) |should| equal_to(['', 'four', 'hi'])

            @fudge.test
            it "just uses parts from parent if it has one when promotes children":
                (self.fake_memoized.expects("url_parts")
                    .with_args(self.parent).returns(['', 'one', 'two'])
                    .next_call().with_args(self.parent2).returns(['four'])
                    )
                
                self.section.url = '/hi'
                self.section.parent = self.parent
                self.section.options.has_attr(promote_children=True)
                self.master.url_parts_value(self.section) |should| equal_to(['', 'one', 'two'])
                
                self.section2.url = 'hi'
                self.section2.parent = self.parent2
                self.section2.options.has_attr(promote_children=True)
                self.master.url_parts_value(self.section2) |should| equal_to(['', 'four'])

        describe "Getting selected":
            before_each:
                self.url = fudge.Fake("url")
                self.path = fudge.Fake("path")
                self.section.url = self.url
            
            @fudge.test
            it "returns (False, []) if no path is provided":
                self.section.parent = None
                self.master.selected_value(self.section, None) |should| equal_to((False, []))
            
            @fudge.test
            it "returns (False, []) if both parent isn't selected and path isn't provided":
                self.section.parent = self.parent
                self.fake_memoized.expects("selected").with_args(self.parent, path=None).returns([False, []])
                self.master.selected_value(self.section, None) |should| equal_to((False, []))
            
            @fudge.test
            it "returns (False, []) if parent isn't selected":
                self.section.parent = self.parent
                self.fake_memoized.expects("selected").with_args(self.parent, path=self.path).returns([False, []])
                self.master.selected_value(self.section, self.path) |should| equal_to((False, []))
            
            @fudge.test
            it "returns (True, path) if promote_children conditional for section is True when url doesn't match start of path":
                self.section.url = 'meh'
                self.section.parent = None
                self.section.options = self.options
                path = ['blah']
                self.options.has_attr(promote_children=True)
                self.master.selected_value(self.section, path) |should| equal_to((True, path))
            
            describe "Looking at path and url":
                before_each:
                    self.section.url = None
                    self.section.parent = None
                    self.section.options = self.options
                    self.options.has_attr(promote_children=False)
                
                @fudge.test
                it "returns (True, path[1:]) if path[0] is '' and url is '/'":
                    tests = [
                          ([''], '/', [])
                        , (['', 'three'], '/', ['three'])
                        , (['', 'five', 'six', 'seven'], '/', ['five', 'six', 'seven'])
                        ]
                    
                    for path, url, leftover in tests:
                        self.section.url = url
                        self.master.selected_value(self.section, path) |should| equal_to((True, leftover))
                
                @fudge.test
                it "returns (True, path[1:]) if path[0] == url":
                    tests = [
                          (['one'], 'one', [])
                        , (['two', 'three'], 'two', ['three'])
                        , (['four', 'five', 'six', 'seven'], 'four', ['five', 'six', 'seven'])
                        ]
                    
                    for path, url, leftover in tests:
                        self.section.url = url
                        self.master.selected_value(self.section, path) |should| equal_to((True, leftover))
                
                @fudge.test
                it "returns (False, []) if path[0] isn't url":
                    tests = [
                          (['one'], 'klj')
                        , (['two', 'three'], 'sdfg')
                        , (['four', 'five', 'six', 'seven'], 'asdf')
                        ]
                    
                    for path, url in tests:
                        self.section.url = url
                        self.master.selected_value(self.section, path) |should| equal_to((False, []))
    
    describe "Getting info":
        before_each:
            self.url = fudge.Fake("url")
            self.path = fudge.Fake("path")
            self.alias = fudge.Fake("alias")
            self.values = fudge.Fake("values")
            self.parent = fudge.Fake("parent")
            self.options = fudge.Fake("options")
            
            self.section = fudge.Fake("section")
            self.fake_memoized = fudge.Fake("memoized")
            self.patched = fudge.patch_object(self.master, 'memoized', self.fake_memoized)
        
        after_each:
            self.patched.restore()
        
        describe "Getting url and alias from a section":
            @fudge.test
            it "yields nothing if active conditional is False":
                self.section.options = self.options
                self.options.expects("conditional").with_args('active', self.request).returns(False)
                list(self.master.iter_section(self.section, self.path)) |should| equal_to([])
            
            @fudge.test
            it "yields section.url, section.alias if no values":
                self.section.url = self.url
                self.section.alias = self.alias
                self.section.options = self.options
                self.section.options.values = None
                self.options.expects("conditional").with_args('active', self.request).returns(True)
                list(self.master.iter_section(self.section, self.path)) |should| equal_to([(self.url, self.alias)])
            
            @fudge.test
            it "yields url, alias for each value if has values":
                url1 = fudge.Fake("url1")
                url2 = fudge.Fake("url2")
                alias1 = fudge.Fake("alias1")
                alias2 = fudge.Fake("alias2")
                things = [(url1, alias1), (url2, alias2)]
                
                self.section.parent = self.parent
                self.section.options = self.options
                self.section.options.values = self.values
                parent_url_parts = fudge.Fake("parent_url_parts")
                self.fake_memoized.expects("url_parts").with_args(self.parent).returns(parent_url_parts)
                self.values.expects("get_info").with_args(self.request, self.path, parent_url_parts).returns(things)
                self.options.expects("conditional").with_args('active', self.request).returns(True)
                list(self.master.iter_section(self.section, self.path)) |should| equal_to(things)
    
        describe "Getting info for each (url, alias) in section":
            before_each:
                self.path = [9, 9, 9]
                self.fake_iter_section = fudge.Fake("iter_section")
                self.patched_iter_section = fudge.patch_object(self.master, 'iter_section', self.fake_iter_section)

                self.section.parent = fudge.Fake("parent")
                self.section.options = fudge.Fake("options")
            
            after_each:
                self.patched_iter_section.restore()
            
            @fudge.test
            it "yields Info object for each (url, alias) for the section":
                self.fake_iter_section.expects_call().with_args(self.section, self.path).returns([(1, 2), (3, 4)])
                result = list(self.master.get_info(self.section, self.path))
                result |should| have(2).infos
                all(type(r) == Info for r in result) |should| be(True)
            
            describe "With each info":
                before_each:
                    self.section.parent = fudge.Fake("parent")
                    self.section.options = fudge.Fake("options")

                def get_info(self, path=None):
                    """Generate one info object and return it"""
                    if path is None:
                        path = self.path
                    
                    (self.fake_iter_section.expects_call()
                        .with_args(self.section, path).returns([(self.url, self.alias)])
                        )
                    results = list(self.master.get_info(self.section, path))
                    results |should| have(1).info
                    return results[0]
                    
                @fudge.test
                it "gives Info the url, alias, section and parent":
                    info = self.get_info(self.path)
                    info.url |should| be(self.url)
                    info.alias |should| be(self.alias)
                    info.section |should| be(self.section)
                
                @fudge.test
                it "gives info selected as method that says whether info can be selected for given path":
                    info = self.get_info([])
                    result = fudge.Fake("result")
                    self.fake_memoized.expects("selected").with_args(info, path=[]).returns(result)
                    info.selected() |should| be(result)
                
                @fudge.test
                it "path given to selected is a copy of the path given to get_info":
                    path = [1, 2, 3]
                    info = self.get_info(path)
                    path.append(4)
                    path[1] = 5
                    result = fudge.Fake("result")
                    self.fake_memoized.expects("selected").with_args(info, path=[1, 2, 3]).returns(result)
                    info.selected() |should| be(result)
                
                @fudge.test
                it "gives info url_parts as method that gets url_parts from info":
                    info = self.get_info()
                    result = fudge.Fake("result")
                    self.fake_memoized.expects("url_parts").with_args(info).returns(result)
                    info.url_parts() |should| be(result)
                
                describe "info.appear":
                    @fudge.test
                    it "method that says whether info exists and is active":
                        info = self.get_info()
                        (self.fake_memoized.remember_order()
                            .expects("exists").with_args(info).returns(True)
                            .expects("active").with_args(info).returns(True)
                            )
                        
                        info.appear() |should| be(True)
                    
                    @fudge.test
                    it "doesn't call active if doesn't exist":
                        info = self.get_info()
                        self.fake_memoized.expects("exists").with_args(info).returns(False)
                        info.appear() |should| be(False)
