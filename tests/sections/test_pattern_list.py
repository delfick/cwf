# coding: spec

from cwf.sections.pattern_list import PatternList
import fudge
import re

describe "PatternList":
    describe "Initialization":
        before_each:
            self.stop_at = fudge.Fake("stop_at")
            self.section = fudge.Fake("section")
            self.include_as = fudge.Fake("include_as")
            self.without_include = fudge.Fake("without_include")
            self.section.has_children = True

        it "sets section, stop_at, include_as and without_include to what's passed in":
            lst = PatternList(self.section
                , stop_at=self.stop_at, include_as=self.include_as, without_include=self.without_include
                )
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

    describe "Determining pattern list":
        before_each:
            self.stop_at = fudge.Fake("stop_at")
            self.section = fudge.Fake("section")
            self.include_as = fudge.Fake("include_as")
            self.without_include = fudge.Fake("without_include")

            self.fake_pattern_list_for = fudge.Fake("pattern_list_for")

            self.lst = type("lst", (PatternList, )
                , { 'pattern_list_for' : self.fake_pattern_list_for
                  }
                )(self.section
                    , stop_at=self.stop_at, include_as=self.include_as, without_include=self.without_include
                    )

        @fudge.patch("cwf.sections.pattern_list.PatternList")
        it "creates a PatternList for each url child of the section and uses pattern_list_for to extract pattern tuples", fakePatternList:
            t1 = fudge.Fake("t1")
            t2 = fudge.Fake("t2")
            t3 = fudge.Fake("t3")
            t4 = fudge.Fake("t4")
            t5 = fudge.Fake("t5")
            t6 = fudge.Fake("t6")

            section1 = fudge.Fake("section1")
            section2 = fudge.Fake("section2")
            section3 = fudge.Fake("section3")

            include_as1 = fudge.Fake("include_as1")
            include_as2 = fudge.Fake("include_as2")
            include_as3 = fudge.Fake("include_as3")

            item1 = fudge.Fake("item1").has_attr(section=section1, include_as=include_as1)
            item2 = fudge.Fake("item2").has_attr(section=section2, include_as=include_as2)
            item3 = fudge.Fake("item3").has_attr(section=section3, include_as=include_as3)

            list1 = fudge.Fake("list1")
            list2 = fudge.Fake("list2")
            list3 = fudge.Fake("list3")
            (fakePatternList.expects_call()
                            .with_args(section1, stop_at=self.stop_at, include_as=include_as1).returns(list1)
                .next_call().with_args(section2, stop_at=self.stop_at, include_as=include_as2).returns(list2)
                .next_call().with_args(section3, stop_at=self.stop_at, include_as=include_as3).returns(list3)
                )

            (self.fake_pattern_list_for.expects_call()
                .with_args(item1, list1).returns((t1, t2))
                .next_call().with_args(item2, list2).returns((t3, ))
                .next_call().with_args(item3, list3).returns((t4, t5, t6))
                )

            self.section.has_attr(url_children=[item1, item2, item3])
            list(self.lst.pattern_list()) |should| equal_to([t1, t2, t3, t4, t5, t6])

    describe "Getting pattern tuples for an item":
        before_each:
            self.item = fudge.Fake("item")
            self.section = fudge.Fake("section")
            self.include_as = fudge.Fake("include_as")

            self.pattern_list = fudge.Fake("pattern_list")

            self.lst_section = fudge.Fake("lst_section")
            self.lst_without_include = fudge.Fake('lst_without_include')
            self.lst = PatternList(self.lst_section, without_include=self.lst_without_include)

        @fudge.patch("cwf.sections.pattern_list.django_include")
        it "yields tuple for django include if item has an include_as", fake_django_include:
            opt1 = fudge.Fake("opt1")
            opt2 = fudge.Fake("opt2")
            path = fudge.Fake("path")
            includer = fudge.Fake("includer")

            self.item.has_attr(include_as=self.include_as)
            self.pattern_list.expects("pattern_tuple_includer").returns((path, (opt1, opt2)))
            fake_django_include.expects_call().with_args(opt1, opt2).returns(includer)

            self.lst.without_include = False
            list(self.lst.pattern_list_for(self.item, self.pattern_list)) |should| equal_to([(path, includer)])

        @fudge.test
        it "yields pattern_tuple from pattern_list if the item's section is the same as this section":
            self.item.has_attr(include_as=None, section=self.lst_section)
            pattern_tuple = fudge.Fake("pattern_tuple")
            self.pattern_list.expects("pattern_tuple").returns(pattern_tuple)
            list(self.lst.pattern_list_for(self.item, self.pattern_list)) |should| equal_to([pattern_tuple])

        @fudge.test
        it "yields nothing if pattern_tuple from pattern_list returns None when item's section is the same as this section":
            self.item.has_attr(include_as=None, section=self.lst_section)
            self.pattern_list.expects("pattern_tuple").returns(None)
            list(self.lst.pattern_list_for(self.item, self.pattern_list)) |should| equal_to([])

        @fudge.test
        it "ignores include_as if without_include is truthy":
            self.item.has_attr(include_as=self.include_as, section=self.lst_section)
            pattern_tuple = fudge.Fake("pattern_tuple")
            self.pattern_list.expects("pattern_tuple").returns(pattern_tuple)
            self.lst.without_include = True
            list(self.lst.pattern_list_for(self.item, self.pattern_list)) |should| equal_to([pattern_tuple])

        @fudge.test
        it "just extracts tuples from the pattern list if neither include_as or current section":
            t1 = fudge.Fake("t1")
            t2 = fudge.Fake("t2")
            t3 = fudge.Fake("t3")

            pattern_list = (t1, t2, t3)
            self.item.has_attr(include_as=None, section=self.section)
            list(self.lst.pattern_list_for(self.item, pattern_list)) |should| equal_to([t1, t2, t3])

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
            url_parts = fudge.Fake("url_parts")

            self.fake_determine_url_parts.expects_call().returns(url_parts)
            self.fake_create_pattern.expects_call().with_args(url_parts).returns(self.pattern)
            self.fake_url_view.expects_call().returns([1, 2])
            (pattern, _, _, _) = self.lst.pattern_tuple()
            pattern |should| be(self.pattern)

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
            (_, view, kwargs, _) = self.lst.pattern_tuple()
            view |should| be(self.view)
            kwargs |should| be(self.kwargs)

        @fudge.test
        it "gets name from self.section":
            self.fake_determine_url_parts.expects_call()
            self.fake_create_pattern.expects_call()
            self.fake_url_view.expects_call().returns([1, 2])
            (_, _, _, name) = self.lst.pattern_tuple()
            name |should| be(self.name)

    describe "Getting pattern tuple for includer":
        before_each:
            self.section = fudge.Fake("section")
            self.include_as = fudge.Fake("include_as")
            self.lst = PatternList(self.section, include_as=self.include_as)

        @fudge.test
        it "returns include_as as a path with leading ^ and trailing /":
            self.section.is_a_stub()
            expected = "^{}/".format(self.include_as)
            path, _ = self.lst.pattern_tuple_includer()
            path |should| equal_to(expected)

        @fudge.test
        it "returns patterns, namespace and app_name from the section":
            patterns = fudge.Fake("patterns")
            app_name = fudge.Fake("app_name")
            namespace = fudge.Fake("namespace")
            url_options = fudge.Fake("url_options")

            # without_include is True so that we get atleast one level of actual patterns
            self.section.expects("patterns").with_args(without_include=True).returns(patterns)

            self.section.has_attr(url_options=url_options)
            url_options.has_attr(namespace=namespace, app_name=app_name)

            _, (ps, ns, an) = self.lst.pattern_tuple_includer()
            ps |should| be(patterns)
            an |should| be(app_name)
            ns |should| be(namespace)

    ########################
    ####   URL UTILITY
    ########################

    describe "Getting pattern for url":
        before_each:
            self.url_parts = fudge.Fake('url_parts')

            self.url_options = fudge.Fake("url_options")
            self.section = fudge.Fake("section").has_attr(url_options=self.url_options, has_children=False)

            self.lst = PatternList(self.section)

        @fudge.test
        it "asks url_options to create patterns from the url_parts":
            pattern = fudge.Fake("pattern")
            self.url_options.expects("create_pattern").with_args(self.url_parts).returns(pattern)
            self.lst.create_pattern(self.url_parts) |should| be(pattern)

    describe "Getting view for url":
        before_each:
            self.url_options = fudge.Fake("url_options")
            self.section = fudge.Fake("section").has_attr(url_options=self.url_options, has_children=False)

            self.lst = PatternList(self.section)

        @fudge.test
        it "asks url_options to get the view for the url and returns nothing if get nothing":
            self.url_options.expects("url_view").with_args(self.section).returns(None)
            self.lst.url_view() |should| be(None)

        @fudge.test
        it "asks url_options to get the view for the url, modifies view using the section and returns view, kwargs":
            view = fudge.Fake("view")
            kwargs = fudge.Fake("kwargs")
            modified_view = fudge.Fake("modified_view")
            self.url_options.expects("url_view").with_args(self.section).returns((view, kwargs))
            self.section.expects("make_view").with_args(view, self.section).returns(modified_view)
            self.lst.url_view() |should| equal_to((modified_view, kwargs))

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
            self.parent = fudge.Fake("parent")
            self.stop_at = fudge.Fake("stop_at")

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
            self.section.parent = self.parent
            self.lst.parent_url_parts() |should| be(parts)
