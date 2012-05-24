# coding: spec

from src.sections.errors import ConfigurationError
from src.sections.section import Section

import fudge
import re

describe "Section":
    describe "Initialisation":
        it "takes in the url, name and parent it is given":
            url = fudge.Fake("url")
            name = fudge.Fake("name")
            parent = fudge.Fake("parent")
            section = Section(url=url, name=name, parent=parent)
            
            section.url |should| be(url)
            section.name |should| be(name)
            section.parent |should| be(parent)
    
    describe "Usage":
        before_each:
            self.url = fudge.Fake("url")
            self.name = fudge.Fake("name")
            self.match = fudge.Fake("match")
            self.new_section = fudge.Fake("new_section")
            
            self.fake_add_child = fudge.Fake("add_child")
            self.fake_make_section = fudge.Fake("make_section")
            self.section = type("Section", (Section, )
                , { 'add_child' : self.fake_add_child
                  , 'make_section' : self.fake_make_section
                  }
                )()
        
        describe "Adding a child":
            it "complains if no url is specified":
                for invalid in (None, "", False, []):
                    with self.assertRaisesRegexp(ConfigurationError, "Use section.first\(\) to add a section with same url as parent"):
                        self.section.add(invalid)
            
            @fudge.test
            it "creates new section and adds as child to the current section":
                (self.fake_make_section.expects_call()
                    .with_args(self.url, self.match, self.name).returns(self.new_section)                
                    )
                
                # Make sure new section is added as a child
                self.fake_add_child.expects_call().with_args(self.new_section)
                self.section.add(self.url, match=self.match, name=self.name)
            
            @fudge.test
            it "returns new section":
                self.fake_make_section.expects_call().returns(self.new_section)
                self.fake_add_child.expects_call().with_args(self.new_section)
                self.section.add(self.url, match=self.match, name=self.name) |should| be(self.new_section)
        
        describe "Adding a first child":
            @fudge.test
            it "defaults url to empty string":
                # Make section gets empty string
                (self.fake_make_section.expects_call()
                    .with_args("", self.match, self.name).returns(self.new_section)                
                    )
                
                # Make sure new section is added as a child
                self.fake_add_child.expects_call().with_args(self.new_section, first=True)
                self.section.first(match=self.match, name=self.name)
            
            @fudge.test
            it "defaults name to name of current section":
                original_name = fudge.Fake("original_name")
                self.section.name = original_name
                
                (self.fake_make_section.expects_call()
                    .with_args(self.url, self.match, original_name).returns(self.new_section)                
                    )
                
                # Make sure new section is added as a child
                self.fake_add_child.expects_call().with_args(self.new_section, first=True)
                self.section.first(self.url, match=self.match)
            
            @fudge.test
            it "creates section with provided url, match and name":
                (self.fake_make_section.expects_call()
                    .with_args(self.url, self.match, self.name).returns(self.new_section)                
                    )
                
                # Make sure new section is added as a child
                self.fake_add_child.expects_call().with_args(self.new_section, first=True)
                self.section.first(self.url, match=self.match, name=self.name)
            
            @fudge.test
            it "adds new section as first child":
                self.fake_make_section.expects_call().returns(self.new_section)
                
                # Make sure new section is added as a child
                self.fake_add_child.expects_call().with_args(self.new_section, first=True)
                self.section.first()
            
            @fudge.test
            it "returns new section":
                self.fake_make_section.expects_call().returns(self.new_section)
                
                # Make sure new section is added as a child
                self.fake_add_child.expects_call()
                self.section.first() |should| be(self.new_section)
        
        describe "Configuring a section":
            before_each:
                self.options = fudge.Fake("Options")
                self.section = type("Section", (Section, ), {'options' : self.options})()
            
            @fudge.test
            it "calls set_everything on options with provided kwargs":
                a = fudge.Fake("a")
                b = fudge.Fake("b")
                c = fudge.Fake("c")
                d = fudge.Fake("d")
                self.options.expects("set_everything").with_args(e=a, f=b, g=c, h=d)
                self.section.configure(e=a, f=b, g=c, h=d) |should| be(self.section)
            
            @fudge.test
            it "returns self":
                self.options.expects("set_everything")
                self.section.configure() |should| be(self.section)
    
    describe "Adding children":
        describe "Making a section":
            before_each:
                self.url = fudge.Fake('url')
                self.name = fudge.Fake('name')
                self.match = fudge.Fake('match')
                self.options = fudge.Fake('options')
                self.section = Section()
            
            @fudge.patch("src.sections.section.Section")
            it "creates a section with provided url and name, and parent as current section", fakeSection:
                new_section = fudge.Fake("new_section")
                self.section.options = self.options
                
                (fakeSection.expects_call()
                    .with_args(url=self.url, name=self.name, parent=self.section)
                    .returns(new_section)
                    )
                
                self.options.provides("clone")
                self.section.make_section(self.url, self.match, self.name) |should| be(new_section)
            
            @fudge.patch("src.sections.section.Section")
            it "gives section a clone of current options with match overriden", fakeSection:
                new_section = fudge.Fake("new_section")
                new_options = fudge.Fake("new_options")
                self.section.options = self.options
                
                fakeSection.expects_call().returns(new_section)
                self.options.expects("clone").with_args(match=self.match).returns(new_options)
                
                self.section.make_section(self.url, self.match, self.name) |should| be(new_section)
                new_section.options |should| be(new_options)
        
        describe "Adopting sections":
            before_each:
                self.fake_add_child = fudge.Fake("add_child")
                self.parent1 = fudge.Fake("parent1")
                self.parent2 = fudge.Fake("parent2")
                self.parent3 = fudge.Fake("parent3")
                self.section1 = fudge.Fake("section1")
                self.section2 = fudge.Fake("section2")
                self.section3 = fudge.Fake("section3")
                
                self.section = type("Section", (Section, ), {'add_child' : self.fake_add_child})()
                
            @fudge.test
            it "sets parent on each section as current section and uses add_child":
                (self.fake_add_child.expects_call()
                    .with_args(self.section1)
                    .next_call().with_args(self.section2)
                    .next_call().with_args(self.section3)
                    )
                
                self.section1.parent = self.parent1
                self.section2.parent = self.parent2
                self.section3.parent = self.parent3
                
                self.section.adopt(self.section1, self.section2, self.section3)
                for section in (self.section1, self.section2, self.section3):
                    section.parent |should| be(self.section)
                
            @fudge.test
            it "uses clone with parent=self if clone=True is specified":
                cloned_section1 = fudge.Fake("cloned_section1")
                cloned_section2 = fudge.Fake("cloned_section2")
                cloned_section3 = fudge.Fake("cloned_section3")
                self.section1.expects('clone').with_args(parent=self.section).returns(cloned_section1)
                self.section2.expects('clone').with_args(parent=self.section).returns(cloned_section2)
                self.section3.expects('clone').with_args(parent=self.section).returns(cloned_section3)
                
                (self.fake_add_child.expects_call()
                    .with_args(cloned_section1)
                    .next_call().with_args(cloned_section2)
                    .next_call().with_args(cloned_section3)
                    )
                
                self.section.adopt(self.section1, self.section2, self.section3, clone=True)
            
            @fudge.test
            it "returns self":
                self.fake_add_child.expects_call()
                self.section2.provides("clone")
                
                self.section.adopt(self.section1) |should| be(self.section)
                self.section.adopt(self.section2, clone=True) |should| be(self.section)
        
        describe "Merging in other sections":
            before_each:
                self.new_section = fudge.Fake("new_section")
                self.new_section._base = None
                self.new_section._children = []
                
                # Objects to represent consider_for_menu booleans
                self.cfm1 = fudge.Fake("cfm1")
                self.cfm2 = fudge.Fake("cfm2")
                
                # Objects to represent the children
                self.child1 = fudge.Fake("child1")
                self.child2 = fudge.Fake("child2")
                
                # Fake out add_child to ensure it is called
                self.fake_add_child = fudge.Fake("add_child")
                self.section = type("Section", (Section, ), {'add_child' : self.fake_add_child})()
            
            @fudge.test
            it "will add clones of children in new section":
                self.new_section._children = [(self.child1, self.cfm1), (self.child2, self.cfm2)]
                
                cloned_child1 = fudge.Fake("cloned_child1")
                cloned_child2 = fudge.Fake("cloned_child2")
                self.child1.expects("clone").with_args(parent=self.section).returns(cloned_child1)
                self.child2.expects("clone").with_args(parent=self.section).returns(cloned_child2)
                
                (self.fake_add_child.expects_call()
                    .with_args(cloned_child1, consider_for_menu=self.cfm1)
                    .next_call().with_args(cloned_child2, consider_for_menu=self.cfm2)
                    )
                
                self.section.merge(self.new_section)
            
            @fudge.test
            it "will replace self._base with None if take_base is true and new section has no base":
                old_base = fudge.Fake("old_base")
                self.section._base = old_base
                self.new_section._base = None
                
                self.section.merge(self.new_section, take_base=True)
                self.section._base |should| be(None)
            
            @fudge.test
            it "will replace self._base with clone of new section base if take_base is true":
                old_base = fudge.Fake("old_base")
                new_base = fudge.Fake("new_base")
                self.section._base = old_base
                self.new_section._base = new_base
                
                cloned_new_base = fudge.Fake("cloned_new_base")
                new_base.expects("clone").with_args(parent=self.section).returns(cloned_new_base)
                
                self.section.merge(self.new_section, take_base=True)
                self.section._base |should| be(cloned_new_base)
            
            @fudge.test
            it "returns self":
                self.section.merge(self.new_section) |should| be(self.section)
                self.section.merge(self.new_section, take_base=True) |should| be(self.section)
                
                self.new_section._base = fudge.Fake("base").expects("clone")
                self.section.merge(self.new_section, take_base=True) |should| be(self.section)
        
        describe "Adding a copy of a section":
            before_each:
                self.new_section = fudge.Fake("new_section")
                self.fake_add_child = fudge.Fake("add_child")
                self.section = type("Section", (Section, ), {'add_child' : self.fake_add_child})()
            
            @fudge.test
            it "creates a clone of the given section with new parent and adds it as a child":
                cloned_section = fudge.Fake("cloned_section")
                self.new_section.expects("clone").with_args(parent=self.section).returns(cloned_section)
                self.fake_add_child.expects_call().with_args(cloned_section)
                self.section.copy(self.new_section) |should| be(self.section)
        
        describe "Adding a section":
            before_each:
                self.section = Section()
                self.section._base = self.original_base = fudge.Fake("original_base")
                
                self.new_section = fudge.Fake("new_section")
                self.consider_for_menu = fudge.Fake("consider_for_menu")
                
            it "adds to self._base if first is True":
                self.section._base |should| be(self.original_base)
                self.section.add_child(self.new_section, first=True, consider_for_menu=self.consider_for_menu)
                self.section._base |should| equal_to((self.new_section, self.consider_for_menu))
                
            it "adds to self._children if first is False":
                self.section._base |should| be(self.original_base)
                self.section._children |should| be_empty
                
                self.section.add_child(self.new_section, first=False, consider_for_menu=self.consider_for_menu)
                self.section._base |should| be(self.original_base)
                self.section._children |should| equal_to([(self.new_section, self.consider_for_menu)])
        
    describe "Options":
        @fudge.patch("src.sections.section.Options")
        it "is lazily loaded", fakeOptions:
            section = Section()
            options = fudge.Fake("options")
            fakeOptions.expects_call().times_called(1).returns(options)
            
            section.options |should| be(options)
            section.options |should| be(options)
        
        @fudge.patch("src.sections.section.Options")
        it "can be set to something else", fakeOptions:
            # Don't put expectations on fakeOptions
            new_options = fudge.Fake("new_options")
            section = Section()
            section.options = new_options
            section.options |should| be(new_options)
    
    describe "Alias":
        before_each:
            self.section = Section()
            self.alias = fudge.Fake("alias")
        
        @fudge.test
        it "uses self.options.alias":
            self.section.options.alias = self.alias
            self.section.alias |should| be(self.alias)
        
        @fudge.test
        it "uses capitialized url if no options.alias":
            url = fudge.Fake("url")
            capitialized_url = fudge.Fake("capitialized_url")
            url.expects("capitalize").returns(capitialized_url)
            
            self.section.url = url
            self.section.options.alias = None
            
            self.section.alias |should| be(capitialized_url)
    
    describe "Children":
        before_each:
            self.cfm = fudge.Fake("cfm")
            self.base = fudge.Fake("base")
            self.child1 = fudge.Fake("child1")
            self.child2 = fudge.Fake("child2")
            
            self.section = Section()
            self.section._base = (self.base, self.cfm)
            self.section._children = [(self.child1, self.cfm), (self.child2, self.cfm)]
            
        it "yields self._base first":
            list(self.section.children)[0] |should| be(self.base)
        
        it "yields all other children after base":
            list(self.section.children) |should| equal_to([self.base, self.child1, self.child2])
        
        it "ignores base if it isn't defined":
            self.section._base = None
            list(self.section.children) |should| equal_to([self.child1, self.child2])
        
        it "works if added via add_child":
            self.section._base = None
            self.section._children = []
            self.section.add_child(self.child1, consider_for_menu=self.cfm)
            self.section.add_child(self.base, first=True)
            self.section.add_child(self.child2)
            list(self.section.children) |should| equal_to([self.base, self.child1, self.child2])        
    
    describe "menu sections":
        before_each:
            self.cfmb = fudge.Fake("cfmb")
            self.cfm1 = fudge.Fake("cfm1")
            self.cfm2 = fudge.Fake("cfm2")
            
            self.base = fudge.Fake("base")
            self.child1 = fudge.Fake("child1")
            self.child2 = fudge.Fake("child2")
            
            self.section = Section()
            self.section._base = (self.base, self.cfmb)
            self.section._children = [(self.child1, self.cfm1), (self.child2, self.cfm2)]
            
        it "yields self._base first":
            list(self.section.menu_sections)[0] |should| be(self.base)
        
        it "yields children after self._base":
            list(self.section.menu_sections) |should| equal_to([self.base, self.child1, self.child2])
        
        it "doesn't yield self._base or children if consider_for_menu is Falsey":
            self.section._base = (self.base, False)
            list(self.section.menu_sections) |should| equal_to([self.child1, self.child2])
            
            self.section._children = [(self.child1, False), (self.child2, False)]
            list(self.section.menu_sections) |should| be_empty
    
    describe "Itering section":
        before_each:
            # iter function to return whatever self.childs is
            # It is used as iter function for self.children
            __iter__ = lambda s: self.childs
            self.children = type("children", (object, ), {'__iter__' : __iter__})()
            self.section = type("Section", (Section, ), {'children' : self.children})()
        
        it "yields self first":
            self.childs = (t for t in [(1, ), (2, ), (3, )])
            list(self.section) |should| equal_to([self.section, 1, 2, 3])
            
        it "yields all children after self":
            self.childs = (t for t in [(1, 2, 3), (4, ), (5, 6, )])
            list(self.section) |should| equal_to([self.section, 1, 2, 3, 4, 5, 6])
    
    describe "Patterns":
        describe "Getting patterns as normal patterns":
            before_each:
                self.fake_pattern_list = fudge.Fake("pattern_list")
                self.section = type("Section", (Section, ), {'pattern_list' : self.fake_pattern_list})()
            
            @fudge.test
            it "uses django patterns factory with self.pattern_list":
                kw1 = fudge.Fake('kw1')
                kw2 = fudge.Fake('kw2')
                kw3 = fudge.Fake('kw3')
                
                p1 = fudge.Fake("p1")
                p2 = fudge.Fake("p2")
                p3 = fudge.Fake("p3")
                
                patterns = fudge.Fake("patterns")
                
                (self.fake_pattern_list.expects_call()
                    .with_args(a=kw1, c=kw2, e=kw3).returns([p1, p2, p3])
                    )
                
                fake_patterns = (fudge.Fake("patterns").expects_call()
                    .with_args('', p1, p2, p3).returns(patterns)
                    )
            
                with fudge.patched_context("src.sections.section", "patterns", fake_patterns):
                    list(self.section.patterns(a=kw1, c=kw2, e=kw3)) |should| equal_to([patterns])
        
        describe "Getting patterns as includes":
            before_each:
                self.app_name = fudge.Fake("app_name")
                self.namespace = fudge.Fake("namespace")
                self.include_as = fudge.Fake("include_as")
                self.include_path = fudge.Fake("include_path")
                
                self.fake_patterns = fudge.Fake("patterns")
                self.fake_include_path = fudge.Fake("include_path")
                self.section = type("Section", (Section, ),
                    { 'patterns' : self.fake_patterns
                    , 'include_path' : self.fake_include_path
                    }
                )()
            
            @fudge.test
            it "returns (path, _) where path is from include_path":
                self.fake_include_path.expects_call().with_args(self.include_as).returns(self.include_path)
                self.fake_patterns.expects_call().returns([])
                path, _ = self.section.include_patterns(self.namespace, self.app_name, self.include_as)
                path |should| be(self.include_path)
            
            @fudge.test
            it "returns (_, includer) where includer is django url include with self.patterns":
                includer = fudge.Fake("includer")
                patterns = fudge.Fake("patterns")
                
                self.fake_include_path.expects_call().returns(self.include_path)
                
                (self.fake_patterns.expects_call()
                    .with_args(children_only=True, stop_at=self.section).returns(patterns)
                    )
                
                fake_include = (fudge.Fake("include").expects_call()
                    .with_args(patterns, self.namespace, self.app_name).returns(includer)
                    )
                
                with fudge.patched_context("src.sections.section", "include", fake_include):
                    _, result = self.section.include_patterns(self.namespace, self.app_name, self.include_as)
                    result |should| be(includer)
        
        describe "Getting pattern list for section itself":
            before_each:
                self.start = fudge.Fake("start")
                self.stop_at = fudge.Fake("stop_at")
                self.children_only = fudge.Fake("children_only")
                
                self.view = fudge.Fake("view")
                self.name = fudge.Fake("name")
                self.kwargs = fudge.Fake("kwargs")
                self.pattern = fudge.Fake("pattern")
                
                self.fake_url_pattern = fudge.Fake("url_pattern")
                self.section = type("Section", (Section, ), {'url_pattern' : self.fake_url_pattern})(name=self.name)
            
            @fudge.test
            it "gets pattern from url_pattern":
                self.fake_url_pattern.expects_call().with_args(self.stop_at, start=self.start).returns(self.pattern)
                fake_url_view = fudge.Fake("url_view").expects_call().returns([1, 2])
                
                with fudge.patched_context(self.section.options, 'url_view', fake_url_view):
                    p, _, _, _ = self.section.pattern_list_first(self.stop_at, self.start)
                    p |should| be(self.pattern)
            
            @fudge.test
            it "gets view and kwargs from options.url_view":
                self.fake_url_pattern.expects_call().returns(self.pattern)
                fake_url_view = (fudge.Fake("url_view").expects_call()
                    .with_args(self.section).returns([self.view, self.kwargs])
                    )
                
                with fudge.patched_context(self.section.options, 'url_view', fake_url_view):
                    _, v, k, _ = self.section.pattern_list_first(self.stop_at, self.start)
                    v |should| be(self.view)
                    k |should| be(self.kwargs)
            
            @fudge.test
            it "also returns self.name":
                self.fake_url_pattern.expects_call().returns(self.pattern)
                fake_url_view = fudge.Fake("url_view").expects_call().returns([1, 2])
                
                with fudge.patched_context(self.section.options, 'url_view', fake_url_view):
                    _, _, _, n = self.section.pattern_list_first(self.stop_at, self.start)
                    n |should| be(self.name)
        
        describe "Getting list of normal patterns":
            before_each:
                self.start = fudge.Fake("start")
                self.stop_at = fudge.Fake("stop_at")
                self.children_only = fudge.Fake("children_only")
                
                self.fake_pattern_list_first = fudge.Fake("pattern_list_first")
                self.section = type("Section", (Section, ), {'pattern_list_first' : self.fake_pattern_list_first})()
            
            describe "With no children":
                before_each:
                    self.section._base = None
                    self.section._children = []
                
                @fudge.test
                it "yields nothing if promoting children":
                    self.section.options.promote_children = True
                    list(self.section.pattern_list()) |should| be_empty
                
                @fudge.test
                it "yields pattern list for only itself if not promoting children":
                    first = fudge.Fake("first")
                    
                    (self.fake_pattern_list_first.expects_call()
                        .with_args(self.stop_at, self.start).returns(first)
                        )
                    
                    self.section.options.promote_children = False
                    list(
                        self.section.pattern_list(self.children_only, self.stop_at, self.start)
                    ) |should| equal_to([first])
            
            describe "With children":
                before_each:
                    self.c1 = fudge.Fake("child1")
                    self.c2 = fudge.Fake("child2")
                    self.c3 = fudge.Fake("cihld3")
                    
                    self.section.add_child(self.c1, first=True)
                    self.section.add_child(self.c2)
                    self.section.add_child(self.c3)
                
                @fudge.test
                it "yields only children if promoting children":
                    p1a = fudge.Fake("pattern1a")
                    p1b = fudge.Fake("pattern1b")
                    p2 = fudge.Fake("pattern2")
                    p3a = fudge.Fake("pattern3a")
                    p3b = fudge.Fake("pattern3b")
                    
                    self.c1.expects("pattern_list").with_args(self.stop_at, start=self.start).returns([p1a, p1b])
                    self.c2.expects("pattern_list").with_args(self.stop_at, start=self.start).returns([p2])
                    self.c3.expects("pattern_list").with_args(self.stop_at, start=self.start).returns([p3a, p3b])
                    
                    self.section.options.promote_children = True
                    pattern_list = list(self.section.pattern_list(stop_at=self.stop_at, start=self.start))
                    pattern_list|should| equal_to([p1a, p1b, p2, p3a, p3b])
                
                @fudge.test
                it "yields itself followed by the children if not promoting children":
                    first = fudge.Fake("first")
                    p1a = fudge.Fake("pattern1a")
                    p1b = fudge.Fake("pattern1b")
                    p2 = fudge.Fake("pattern2")
                    p3a = fudge.Fake("pattern3a")
                    p3b = fudge.Fake("pattern3b")
                    
                    self.c1.expects("pattern_list").with_args(self.stop_at, start=self.start).returns([p1a, p1b])
                    self.c2.expects("pattern_list").with_args(self.stop_at, start=self.start).returns([p2])
                    self.c3.expects("pattern_list").with_args(self.stop_at, start=self.start).returns([p3a, p3b])
                    
                    (self.fake_pattern_list_first.expects_call()
                        .with_args(self.stop_at, self.start).returns(first)
                        )
                    
                    self.section.options.promote_children = False
                    pattern_list = list(self.section.pattern_list(self.children_only, stop_at=self.stop_at, start=self.start))
                    pattern_list|should| equal_to([first, p1a, p1b, p2, p3a, p3b])
    
    describe "Url creation":
        describe "Getting pattern for url":
            before_each:
                self.end = fudge.Fake("end")
                self.stop_at = fudge.Fake("stop_at")
                self.url_parts = fudge.Fake('url_parts')
                
                self.fake_determine_url_parts = fudge.Fake("determine_url_parts")
                self.section = type("Section", (Section, ), {'determine_url_parts' : self.fake_determine_url_parts})()
            
            @fudge.test
            it "asks options to create patterns from the url_parts determine_url_parts returns":
                result = fudge.Fake("result")
                fake_create_pattern = (fudge.Fake("create_pattern").expects_call()
                    .with_args(self.url_parts, end=self.end).returns(result)
                    )
                
                self.fake_determine_url_parts.expects_call().with_args(self.stop_at).returns(self.url_parts)
                
                with fudge.patched_context(self.section.options, 'create_pattern', fake_create_pattern):
                    self.section.url_pattern(self.stop_at, self.end) |should| be(result)
                
        describe "Getting path for pattern include":
            before_each:
                self.fake_url_pattern = fudge.Fake("url_pattern")
                self.section = type("Section", (Section, ), {'url_pattern' : self.fake_url_pattern})()
                
            describe "When include_as is specified":
                @fudge.test
                it "returns include_as":
                    include_as = "^blah/"
                    self.section.include_path(include_as) |should| equal_to("^blah/")
                
                @fudge.test
                it "ensures only one caret at the start":
                    include_as = "^^^^^^^blah/"
                    self.section.include_path(include_as) |should| equal_to("^blah/")
                
                @fudge.test
                it "ensures only one slash at the end":
                    include_as = "^blah/////"
                    self.section.include_path(include_as) |should| equal_to("^blah/")
                
                @fudge.test
                it "ensures both prepend with caret and append with slash":
                    include_as = "blah"
                    self.section.include_path(include_as) |should| equal_to("^blah/")
                
            describe "When include_as is not specified":
                @fudge.test
                it "defaults to asking url_pattern":
                    result = fudge.Fake("result")
                    (self.fake_url_pattern.expects_call()
                        .with_args(stop_at=self.section, end=False, start=False).returns(result)
                        )
                    self.section.include_path() |should| be(result)
        
        describe "Getting different parts that make up the url":
            describe "Getting own url part":
                before_each:
                    self.url = fudge.Fake("url")
                    self.section = Section(self.url)
                
                it "returns self.url if not a matching section":
                    self.section.options.match = False
                    self.section.own_url_part() |should| be(self.url)
                    
                it "returns named captured group if a matching section":
                    self.section.options.match = fudge.Fake("thematch")
                    self.section.own_url_part() |should| equal_to("(?P<fake:thematch>fake:url)")
                    
                    self.section.url = 'abc'
                    self.section.options.match = 'match'
                    regex = self.section.own_url_part()
                    
                    m = re.match(regex, 'abc')
                    m.groupdict()['match'] |should| equal_to("abc")
            
            describe "Getting url parts from parent":
                before_each:
                    self.p1 = fudge.Fake("p1")
                    self.p2 = fudge.Fake("p2")
                    self.parts = [self.p1, self.p2]
                    self.stop_at = fudge.Fake("stop_at")
                    
                    self.parent = fudge.Fake("parent")
                    self.section = Section(parent=self.parent)
                
                it "returns nothing if no parent":
                    self.section.parent = None
                    self.section.parent_url_parts(None) |should| be_empty
                
                it "returns nothing if self is stop_at":
                    self.section.parent_url_parts(self.section) |should| be_empty
                
                @fudge.test
                it "returns result of asking parent for url_parts if parent and not stopping at this section":
                    self.parent.expects("determine_url_parts").with_args(self.stop_at).returns(self.parts)
                    self.section.parent_url_parts(self.stop_at) |should| equal_to(self.parts)
                
                @fudge.test
                it "can modify result without affecting url_parts of the parent":
                    self.parent.expects("determine_url_parts").with_args(self.stop_at).returns(self.parts)
                    parts = self.section.parent_url_parts(self.stop_at)
                    parts |should| equal_to(self.parts)
                    
                    parts.append(1)
                    parts |should_not| equal_to(self.parts)
                    parts |should| equal_to([self.p1, self.p2, 1])
                    self.parts |should| equal_to([self.p1, self.p2])
            
            describe "Getting combination of parent and self":
                before_each:
                    self.p1 = fudge.Fake("p1")
                    self.p2 = fudge.Fake("p2")
                    self.parts = [self.p1, self.p2]
                    self.stop_at = fudge.Fake("stop_at")
                    
                    self.fake_own_url_part = fudge.Fake("own_url_part")
                    self.fake_parent_url_parts = fudge.Fake("parent_url_parts")
                    
                    self.section = type("Section", (Section, ),
                        { 'own_url_part' : self.fake_own_url_part
                        , 'parent_url_parts' : self.fake_parent_url_parts
                        }
                    )()
                
                @fudge.test
                it "returns self._url_parts if already defined":
                    url_parts = fudge.Fake("url_parts")
                    self.section._url_parts = url_parts
                    self.section.determine_url_parts() |should| be(url_parts)
                    self.section.determine_url_parts(self.stop_at) |should| be(url_parts)
                
                @fudge.test
                it "returns parent url parts appended with own url part":
                    own = fudge.Fake("own")
                    self.fake_own_url_part.expects_call().returns(own)
                    self.fake_parent_url_parts.expects_call().with_args(self.stop_at).returns(self.parts)
                    self.section.determine_url_parts(self.stop_at) |should| equal_to([self.p1, self.p2, own])
    
    describe "Cloning":
        @fudge.test
        it "defaults url, name and parent to values on the section":
            url = fudge.Fake("url")
            name = fudge.Fake("name")
            parent = fudge.Fake("parent")
            
            section = Section(url, name, parent)
            
            new = fudge.Fake("new")
            fakeSection = (fudge.Fake("Section").expects_call()
                .with_args(url=url, name=name, parent=parent).returns(new)
                )
            
            fake_options = fudge.Fake("options").expects("clone")
            section.options = fake_options
            
            with fudge.patched_context("src.sections.section", "Section", fakeSection):
                section.clone() |should| be(new)
            
        it "doesn't override url, name or parent":
            url = fudge.Fake("url")
            name = fudge.Fake("name")
            parent = fudge.Fake("parent")
            section = Section(url, name, parent)
            
            new_url = fudge.Fake("new_url")
            new_name = fudge.Fake("new_name")
            new_parent = fudge.Fake("new_parent")
            
            new = fudge.Fake("new")
            fakeSection = (fudge.Fake("Section").expects_call()
                .with_args(url=new_url, name=new_name, parent=new_parent).returns(new)
                )
            
            fake_options = fudge.Fake("options").expects("clone")
            section.options = fake_options
            
            with fudge.patched_context("src.sections.section", "Section", fakeSection):
                section.clone(url=new_url, name=new_name, parent=new_parent) |should| be(new)
            
        it "creates a clone of options for the new section":
            section = Section()
            new_options = fudge.Fake("new")
            fake_options = fudge.Fake("options").expects("clone").with_args(all=True).returns(new_options)
            section.options = fake_options
            section.clone().options |should| be(new_options)
            
        it "returns new section":
            a = fudge.Fake("a")
            b = fudge.Fake("b")
            new = fudge.Fake("new")
            name = fudge.Fake("name")
            parent = fudge.Fake("parent")
            new_url = fudge.Fake("new_url")
            section = Section(name=name, parent=parent)
            
            fakeSection = (fudge.Fake("Section").expects_call()
                .with_args(url=new_url, name=name, parent=parent, a=a, b=b).returns(new)
                )
            
            fake_options = fudge.Fake("options").expects("clone")
            section.options = fake_options
            
            with fudge.patched_context("src.sections.section", "Section", fakeSection):
                section.clone(url=new_url, a=a, b=b) |should| be(new)
    
    describe "Getting root ancestor":
        it "returns itself if no parent":
            section = Section(parent=None)
            section.rootAncestor() |should| be(section)
        
        it "looks at chain of parents to find root ancestor":
            p1 = fudge.Fake("p1")
            p2 = fudge.Fake("p2")
            p3 = fudge.Fake("p3")
            
            p1.parent = None
            p2.parent = None
            p3.parent = None
            
            section = Section(parent=p1)
            section.rootAncestor() |should| be(p1)
            
            p1.parent = p2
            section.rootAncestor() |should| be(p2)
            
            p2.parent = p3
            section.rootAncestor() |should| be(p3)
        
        it "copes with circular dependencies":
            p1 = fudge.Fake("p1")
            p2 = fudge.Fake("p2")
            
            p1.parent = p2
            p2.parent = p1
            section = Section(parent=p1)
            section.rootAncestor() |should| be(p2)
    
    describe "Determining if reachable":
        before_each:
            self.request = fudge.Fake("request")
            self.section = Section()
        
        @fudge.test
        it "returns False if there is a parent and parent isn't reachable":
            parent = fudge.Fake("parent").expects("reachable").with_args(self.request).returns(False)
            self.section.parent = parent
            self.section.reachable(self.request) |should| be(False)
                
        @fudge.test
        it "returns whether section is reachable if no parent":
            result = fudge.Fake("result")
            self.section.parent = None
            
            fake_reachable = fudge.Fake("reachable").expects_call().returns(result)
            with fudge.patched_context(self.section.options, 'reachable', fake_reachable):
                self.section.reachable(self.request) |should| be(result)
        
        @fudge.test
        it "returns whether section is reachable if parent and parent is reachable":
            result = fudge.Fake("result")
            
            parent = fudge.Fake("parent").expects("reachable").with_args(self.request).returns(True)
            self.section.parent = parent
            
            fake_reachable = fudge.Fake("reachable").expects_call().returns(result)
            with fudge.patched_context(self.section.options, 'reachable', fake_reachable):
                self.section.reachable(self.request) |should| be(result)
