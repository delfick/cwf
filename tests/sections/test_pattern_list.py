# coding: spec

from cwf.sections.pattern_list import PatternList
import fudge
import re

describe "PatternList":
    describe "Initialization":
        before_each:
            self.start = fudge.Fake("start")
            self.stop_at = fudge.Fake("stop_at")
            self.section = fudge.Fake("section")
            self.include_as = fudge.Fake("include_as")
            self.without_include = fudge.Fake("without_include")
            self.section.has_children = True
        
        it "sets section, start, stop_at, include_as and without_include to what's passed in":
            lst = PatternList(self.section
                , start=self.start, stop_at=self.stop_at, include_as=self.include_as, without_include=self.without_include
                )
            lst.start |should| be(self.start)
            lst.stop_at |should| be(self.stop_at)
            lst.section |should| be(self.section)
            lst.include_as |should| be(self.include_as)
            lst.without_include |should| be(self.without_include)
        
        it "sets stop_at to section if passed in as None or not passed in":
            PatternList(self.section).stop_at |should| be(self.section)
            PatternList(self.section, stop_at=None).stop_at |should| be(self.section)
    
    describe "iter":
        before_each:
            self.section = fudge.Fake("section")
            self.section.has_children = True
            self.fake_pattern_list = fudge.Fake("pattern_list")
            self.lst = type("Lst", (PatternList, ), {"pattern_list" : self.fake_pattern_list})(self.section)
        
        @fudge.test
        it "returns result of pattern_list when iterating":
            one = fudge.Fake("one")
            two = fudge.Fake("two")
            three = fudge.Fake("three")
            self.fake_pattern_list.expects_call().returns(iter([one, two, three]))
            list(self.lst) |should| equal_to([one, two, three])    

    describe "Getting pattern list":
        before_each:
            self.child1 = fudge.Fake("child1")
            self.child2 = fudge.Fake("child2")
            
            self.stop_at = fudge.Fake("stop_at")
            self.section = fudge.Fake("section")
            self.section.has_children = False
            
            self.fake_pattern_tuple = fudge.Fake("pattern_tuple")
            self.lst_kls = type("Lst", (PatternList, ), {'pattern_tuple' : self.fake_pattern_tuple})
        
        @fudge.test
        it "returns result of pattern_tuple if child is the section":
            result = fudge.Fake("result")
            self.fake_pattern_tuple.expects_call().returns(result)
            self.section.url_children = [self.section]
            list(self.lst_kls(self.section).pattern_list()) |should| equal_to([result])
        
        @fudge.test
        it "yields nothing if result of pattern_tuple if is None":
            self.fake_pattern_tuple.expects_call().returns(None)
            self.section.url_children = [self.section]
            list(self.lst_kls(self.section).pattern_list()) |should| equal_to([])
        
        @fudge.patch("cwf.sections.pattern_list.PatternList")
        it "returns all yielded from itering a PatternList from child if not the section", fakePatternList:
            u1 = fudge.Fake("u1")
            u2 = fudge.Fake("u2")
            u3 = fudge.Fake("u3")
            u4 = fudge.Fake("u4")
            self.section.url_children = [self.child1, self.child2]
            (fakePatternList.expects_call()
                .with_args(self.child1, start=False, stop_at=self.stop_at).returns([u1, u2])
                .next_call().with_args(self.child2, start=False, stop_at=self.stop_at).returns([u3, u4])
                )
            
            list(self.lst_kls(self.section, stop_at=self.stop_at).pattern_list()) |should| equal_to([u1, u2, u3, u4])
        
        @fudge.patch("cwf.sections.pattern_list.PatternList")
        it "works on multiple children", fakePatternList:
            u1 = fudge.Fake("u1")
            u2 = fudge.Fake("u2")
            u3 = fudge.Fake("u3")
            u4 = fudge.Fake("u4")
            result = fudge.Fake("result")
            self.fake_pattern_tuple.expects_call().returns(result)
            
            self.section.url_children = [self.child1, self.section, self.child2]
            (fakePatternList.expects_call()
                .with_args(self.child1, start=False, stop_at=self.stop_at).returns([u1, u2])
                .next_call().with_args(self.child2, start=False, stop_at=self.stop_at).returns([u3, u4])
                )
            
            list(self.lst_kls(self.section, stop_at=self.stop_at).pattern_list()) |should| equal_to([u1, u2, result, u3, u4])
    
    describe "Determining pattern tuple":
        before_each:
            self.view = fudge.Fake("view")
            self.name = fudge.Fake("name")
            self.kwargs = fudge.Fake("kwargs")
            self.pattern = fudge.Fake("pattern")
            self.section = fudge.Fake("section")
            self.section.name = self.name
            self.section.has_children = False
            
            self.fake_url_view = fudge.Fake("url_view")
            self.fake_create_pattern = fudge.Fake("create_pattern")
            self.fake_determine_url_parts = fudge.Fake("determine_url_parts")
            self.lst = type("Lst", (PatternList, ), 
                { 'url_view' : self.fake_url_view
                , 'create_pattern' : self.fake_create_pattern
                , 'determine_url_parts' : self.fake_determine_url_parts
                }
            )(self.section)
        
        @fudge.test
        it "gets pattern from self.create_pattern":
            end = fudge.Fake("end")
            start = fudge.Fake("start")
            url_parts = fudge.Fake("url_parts")
            
            self.lst.end = end
            self.lst.start = start
            self.fake_determine_url_parts.expects_call().returns(url_parts)
            self.fake_create_pattern.expects_call().with_args(url_parts, start, end).returns(self.pattern)
            self.fake_url_view.expects_call().returns([1, 2])
            section, (pattern, _, _, _) = self.lst.pattern_tuple()
            pattern |should| be(self.pattern)
            section |should| be(self.section)
            
        @fudge.test
        it "returns None if url_view returns None":
            self.fake_determine_url_parts.expects_call()
            self.fake_create_pattern.expects_call()
            self.fake_url_view.expects_call().returns(None)
            self.lst.pattern_tuple() |should| be(None)
            
        @fudge.test
        it "gets view and kwargs from self.url_view()":
            self.fake_determine_url_parts.expects_call()
            self.fake_create_pattern.expects_call()
            self.fake_url_view.expects_call().returns([self.view, self.kwargs])
            section, (_, view, kwargs, _) = self.lst.pattern_tuple()
            view |should| be(self.view)
            kwargs |should| be(self.kwargs)
            section |should| be(self.section)
        
        @fudge.test
        it "gets name from self.section":
            self.fake_determine_url_parts.expects_call()
            self.fake_create_pattern.expects_call()
            self.fake_url_view.expects_call().returns([1, 2])
            section, (_, _, _, name) = self.lst.pattern_tuple()
            name |should| be(self.name)
            section |should| be(self.section)
    
    describe "Getting path for pattern include":
        before_each:
            self.end = fudge.Fake("end")
            self.path = fudge.Fake("path")
            self.start = fudge.Fake("start")
            self.section = fudge.Fake("section")
            self.section.has_children = False
            
            self.fake_create_pattern = fudge.Fake("create_pattern")
            self.fake_determine_url_parts = fudge.Fake("determine_url_parts")
            self.lst = type("Lst", (PatternList, ),
                { 'create_pattern' : self.fake_create_pattern
                , 'determine_url_parts' : self.fake_determine_url_parts
                }
            )(self.section)
            
        def get_path(self, include_as):
            """Call include_path with provided include_as and self.start and self.end"""
            return self.lst.include_path(include_as, start=self.start, end=self.end)
        
        def set_create_pattern_expectation(self, url_parts):
            """
                Set expectation for create_pattern to be called with url_parts supplied and self.start and self.end
                And that it returns self.path
            """
            self.fake_create_pattern.expects_call().with_args(url_parts, start=self.start, end=self.end).returns(self.path)
        
        describe "When include_as is specified":
            @fudge.test
            it "passes include_as into create_pattern":
                include_as = "blah"
                self.set_create_pattern_expectation([include_as])
                self.get_path(include_as) |should| equal_to(self.path)
            
            @fudge.test
            it "ensures no caret at the start":
                include_as = "^^^^^^^blah/"
                self.set_create_pattern_expectation(["blah"])
                self.get_path(include_as) |should| equal_to(self.path)
            
            @fudge.test
            it "ensures no slash at the end":
                include_as = "^blah/////"
                self.set_create_pattern_expectation(["blah"])
                self.get_path(include_as) |should| equal_to(self.path)
            
        describe "When include_as is not specified":
            @fudge.test
            it "gets url_parts from determine_url_parts":
                url_parts = fudge.Fake("url_parts")
                self.fake_determine_url_parts.expects_call().returns(url_parts)
                self.set_create_pattern_expectation(url_parts)
                self.get_path(None) |should| equal_to(self.path)
        
    ########################
    ####   URL UTILITY
    ########################

    describe "Getting pattern for url":
        before_each:
            self.end = fudge.Fake("end")
            self.start = fudge.Fake("start")
            self.url_parts = fudge.Fake('url_parts')

            self.url_options = fudge.Fake("url_options")
            self.section = fudge.Fake("section").has_attr(url_options=self.url_options, has_children=False)

            self.lst = PatternList(self.section)
        
        @fudge.test
        it "asks url_options to create patterns from the url_parts, start and end":
            pattern = fudge.Fake("pattern")
            self.url_options.expects("create_pattern").with_args(self.url_parts, start=self.start, end=self.end).returns(pattern)
            self.lst.create_pattern(self.url_parts, self.start, self.end) |should| be(pattern)

    describe "Getting view for url":
        before_each:
            self.url_options = fudge.Fake("url_options")
            self.section = fudge.Fake("section").has_attr(url_options=self.url_options, has_children=False)

            self.lst = PatternList(self.section)
        
        @fudge.test
        it "asks url_options to get the view for the url":
            view = fudge.Fake("view")
            self.url_options.expects("url_view").with_args(self.section).returns(view)
            self.lst.url_view() |should| be(view)

    describe "Getting url part":
        before_each:
            self.url = fudge.Fake("url")
            self.url_options = fudge.Fake("url_options")
            self.section = fudge.Fake("section").has_attr(url_options=self.url_options, url=self.url, has_children=False)
            self.lst = PatternList(self.section)
        
        it "returns section.url if not a matching section":
            self.url_options.has_attr(match=False)
            self.lst.url_part() |should| be(self.url)
        
        it "returns named captured group if a matching section":
            self.url_options.has_attr(match = fudge.Fake("thematch"))
            self.lst.url_part() |should| equal_to("(?P<fake:thematch>fake:url)")
            
            self.section.has_attr(url='abc')
            self.url_options.has_attr(match='match')
            regex = self.lst.url_part()
            m = re.match(regex, 'abc')
            m.groupdict()['match'] |should| equal_to("abc")

    describe "Determining all url parts":
        before_each:
            self.section = fudge.Fake("section").has_attr(has_children=False)
            self.fake_url_part = fudge.Fake("url_part")
            self.fake_parent_url_parts = fudge.Fake("parent_url_parts")
            self.lst = type("PatternList", (PatternList, ),
                { 'url_part' : self.fake_url_part
                , 'parent_url_parts' : self.fake_parent_url_parts
                }
                )(self.section)
        
        @fudge.test
        it "returns self._url_parts if already defined":
            url_parts = fudge.Fake("url_parts")
            self.lst._url_parts = url_parts
            self.lst.determine_url_parts() |should| be(url_parts)
        
        @fudge.test
        it "returns parent url parts appended section's own url part if not already determined":
            p1 = fudge.Fake("p1")
            p2 = fudge.Fake("p2")
            own = fudge.Fake("own")

            self.fake_url_part.expects_call().returns(own)
            self.fake_parent_url_parts.expects_call().returns([p1, p2])

            self.lst.determine_url_parts() |should| equal_to([p1, p2, own])
            self.lst._url_parts |should| equal_to([p1, p2, own])

        @fudge.test
        it "uses include_as instead of parent url parts if defined":
            ia = fudge.Fake("ia")
            own = fudge.Fake("own")

            self.fake_url_part.expects_call().returns(own)

            self.lst.include_as = ia
            self.lst.determine_url_parts() |should| equal_to([ia, own])
            self.lst._url_parts |should| equal_to([ia, own])

        @fudge.test
        it "doesn't add own url part if it's an empty string":
            ia = fudge.Fake("ia")
            p1 = fudge.Fake("p1")
            p2 = fudge.Fake("p2")
            self.fake_url_part.expects_call().returns('')
            self.fake_parent_url_parts.expects_call().returns([p1, p2])

            # Using parent url parts, doesn't add on ''
            self.lst.determine_url_parts() |should| equal_to([p1, p2])
            self.lst._url_parts |should| equal_to([p1, p2])
            del self.lst.__dict__['_url_parts']

            # Using include_as, doesn't add on ''
            self.lst.include_as = ia
            self.lst.determine_url_parts() |should| equal_to([ia])
            self.lst._url_parts |should| equal_to([ia])

    describe "Getting url parts from parent":
        before_each:
            self.stop_at = fudge.Fake("stop_at")

            self.parent = fudge.Fake("parent")
            self.parent_options = fudge.Fake("parent_options")
            self.parent.options = self.parent_options

            self.section = fudge.Fake("section").has_attr(has_children=False)
            self.lst = PatternList(self.section, stop_at=self.stop_at)
        
        it "returns nothing if no parent":
            self.section.parent = None
            self.lst.parent_url_parts() |should| be_empty
        
        it "returns nothing if section is stop_at":
            self.section.parent = self.parent
            self.lst.stop_at = self.section
            self.lst.parent_url_parts() |should| be_empty
        
        @fudge.patch("cwf.sections.pattern_list.PatternList")
        it "creates a new PatternList for the parent and returns result of determine_url_parts", fakePatternList:
            parts = fudge.Fake("parts")
            pattern_list = fudge.Fake("pattern_list").expects("determine_url_parts").returns(parts)
            fakePatternList.expects_call().with_args(self.parent, stop_at=self.stop_at).returns(pattern_list)
            self.parent_options.has_attr(promote_children=False)
            self.section.parent = self.parent
            self.lst.parent_url_parts() |should| be(parts)

        @fudge.patch("cwf.sections.pattern_list.PatternList")
        it "ignores last url part if parent promotes it's children", fakePatternList:
            p1 = fudge.Fake("p1")
            p2 = fudge.Fake("p2")
            p3 = fudge.Fake("p3")
            parts = [p1, p2, p3]
            pattern_list = fudge.Fake("pattern_list").expects("determine_url_parts").returns(parts)

            fakePatternList.expects_call().with_args(self.parent, stop_at=self.stop_at).returns(pattern_list)

            self.section.parent = self.parent
            self.parent_options.has_attr(promote_children=True)
            self.lst.parent_url_parts() |should| equal_to([p1, p2])
