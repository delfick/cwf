# coding: spec

from src.sections.errors import ConfigurationError
from src.sections.section import Section

from contextlib import contextmanager
from django.http import Http404
import fudge

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
                self.fake_copy = fudge.Fake("copy")
                self.fake_add_child = fudge.Fake("add_child")

                self.parent1 = fudge.Fake("parent1")
                self.parent2 = fudge.Fake("parent2")
                self.parent3 = fudge.Fake("parent3")
                self.section1 = fudge.Fake("section1")
                self.section2 = fudge.Fake("section2")
                self.section3 = fudge.Fake("section3")
                
                self.section = type("Section", (Section, ),
                    { 'copy' : self.fake_copy
                    , 'add_child' : self.fake_add_child
                    }
                )()
            
            @fudge.test
            it "returns self": 
                self.fake_copy.expects_call()   
                self.fake_add_child.expects_call()         
                self.section.adopt(self.section1) |should| be(self.section)
                self.section.adopt(self.section2, clone=True) |should| be(self.section)
            
            describe "Without cloning":
                @fudge.test
                it "sets parent on each section as current section and uses add_child":
                    consider_for_menu = fudge.Fake("consider_for_menu")
                    (self.fake_add_child.expects_call()
                        .with_args(self.section1, consider_for_menu=consider_for_menu)
                        .next_call().with_args(self.section2, consider_for_menu=consider_for_menu)
                        .next_call().with_args(self.section3, consider_for_menu=consider_for_menu)
                        )
                    
                    self.section1.parent = self.parent1
                    self.section2.parent = self.parent2
                    self.section3.parent = self.parent3
                    
                    self.section.adopt(self.section1, self.section2, self.section3, consider_for_menu=consider_for_menu)
                    for section in (self.section1, self.section2, self.section3):
                        section.parent |should| be(self.section)
            
            describe "With cloning":
                @fudge.test
                it "uses self.copy on each section":     
                    consider_for_menu = fudge.Fake("consider_for_menu")               
                    (self.fake_copy.expects_call()
                        .with_args(self.section1, consider_for_menu=consider_for_menu)
                        .next_call().with_args(self.section2, consider_for_menu=consider_for_menu)
                        .next_call().with_args(self.section3, consider_for_menu=consider_for_menu)
                        )
                    
                    self.section.adopt(self.section1, self.section2, self.section3
                        , clone=True
                        , consider_for_menu=consider_for_menu
                        )
        
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
                
                # Fake copy for the section to test
                self.fake_copy = fudge.Fake("copy")
                self.section = type("Section", (Section, ), { 'copy' : self.fake_copy})()
            
            @fudge.test
            it "returns self":
                self.fake_copy.expects_call()

                self.section.merge(self.new_section) |should| be(self.section)
                self.section.merge(self.new_section, take_base=True) |should| be(self.section)
                
                new_base = fudge.Fake("new_base")
                self.new_section._base = (new_base, True)
                self.section.merge(self.new_section, take_base=True) |should| be(self.section)

            @fudge.test
            it "will copy everything in new section's _children":
                self.new_section._children = [(self.child1, self.cfm1), (self.child2, self.cfm2)]

                (self.fake_copy.expects_call()
                    .with_args(self.child1, consider_for_menu=self.cfm1)
                    .next_call().with_args(self.child2, consider_for_menu=self.cfm2)
                    )
                
                self.section.merge(self.new_section)
            
            describe "Using take_base":
                @fudge.test
                it "will not replace _base if new section has no base":
                    old_base = fudge.Fake("old_base")
                    self.section._base = (old_base, True)
                    self.section.merge(self.new_section, take_base=True)
                    self.section._base |should| equal_to((old_base, True))

                @fudge.test
                it "will not replace _base if new section has base but take_base is False":
                    old_base = fudge.Fake("old_base")
                    new_base = fudge.Fake("new_base")

                    self.section._base = (old_base, True)
                    self.new_section._base = (new_base, True)

                    self.section.merge(self.new_section, take_base=False)
                    self.section._base |should| equal_to((old_base, True))
            
                @fudge.test
                it "will replace copy base from new section if it has a base":
                    old_base = fudge.Fake("old_base")
                    new_base = fudge.Fake("new_base")
                    new_section = Section()
                    consider_for_menu = fudge.Fake("consider_for_menu")

                    self.section.add_child(old_base, first=True)
                    new_section.add_child(new_base, first=True, consider_for_menu=consider_for_menu)

                    # Copy will add the a clone of the new base
                    self.fake_copy.expects_call().with_args(new_base, first=True, consider_for_menu=consider_for_menu)
                    self.section.merge(new_section, take_base=True)
        
        describe "Adding a copy of a section":
            before_each:
                self.new_section = fudge.Fake("new_section")
                self.fake_add_child = fudge.Fake("add_child")
                self.section = type("Section", (Section, ), {'add_child' : self.fake_add_child})()
            
            @fudge.test
            it "creates a clone of the given section with new parent and adds it as a child after merging with original":
                first = fudge.Fake("first")
                consider_for_menu = fudge.Fake("consider_for_menu")

                # Cloned section is merged with original to get the children
                cloned_section = (fudge.Fake("cloned_section").expects("merge")
                    .with_args(self.new_section, take_base=True)
                    )

                # Section to copy is cloned before added
                self.new_section.expects("clone").with_args(parent=self.section).returns(cloned_section)

                # Clone is added as a child along with first and consider_for_menu passed into copy
                self.fake_add_child.expects_call().with_args(cloned_section
                    , first=first, consider_for_menu=consider_for_menu
                    )

                self.section.copy(self.new_section, first=first, consider_for_menu=consider_for_menu) |should| be(self.section)
        
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

            it "returns the section being added":
                self.section.add_child(self.new_section, first=True) |should| be(self.new_section)
                self.section.add_child(self.new_section, first=False) |should| be(self.new_section)
        
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
        
    describe "Url Options":
        before_each:
            self.base = Section()
            self.base_options = self.base.options

            self.section = Section()
            self.section_options = self.section.options

        it "returns options on _base if defined":
            self.section.add_child(self.base, first=True)
            self.section.url_options |should| be(self.base.options)

        it "returns options on section if no _base":
            self.section.url_options |should| be(self.section_options)
    
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

    describe "Determining url children":
        before_each:
            self.section = Section()

        @contextmanager
        def using_children(self, section, children):
            patched = fudge.patch_object(section, 'children', children)
            yield section
            patched.restore()

        it "yields all children first before itself":
            c1 = fudge.Fake("child1")
            c2 = fudge.Fake("child2")
            c3 = fudge.Fake("child3")
            with self.using_children(self.section, [c1, c2, c3]):
                list(self.section.url_children) |should| equal_to([c1, c2, c3, self.section])

        it "yields just itself if no children":
            list(self.section.url_children) |should| equal_to([self.section])
    
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

    describe "Determining if section has children":
        @contextmanager
        def using_children(self, section, children):
            patched = fudge.patch_object(section, 'children', children)
            yield section
            patched.restore()

        it "returns whether section has any children":
            section = Section()

            def yielded_with_children():
                yield 1
                yield 2

            def yielded_without_children():
                if False:
                    yield 1

            with self.using_children(section, yielded_with_children()) as sect:
                sect.has_children |should| be(True)

            with self.using_children(section, yielded_without_children()) as sect:
                sect.has_children |should| be(False)

            with self.using_children(section, [1, 2]) as sect:
                sect.has_children |should| be(True)

            with self.using_children(section, []) as sect:
                sect.has_children |should| be(False)

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

    describe "Makinga view for patterns":
        before_each:
            self.request = fudge.Fake("request")
            self.view_result = fudge.Fake("view_result")
            self.fake_reachable = fudge.Fake("reachable")
            self.section = type("Section", (Section, ), {'reachable' : self.fake_reachable})()

        def view(self, request, a, b, c, d):
            a |should| be(1)
            b |should| be(2)
            c |should| be(False)
            d |should| be(True)
            return self.view_result

        it "will set section on the request object":
            self.fake_reachable.expects_call().returns(True)
            self.request |should_not| respond_to('section')
            self.section.make_view(self.view, self.section)(self.request, 1, 2, d=True, c=False)
            self.request.section |should| be(self.section)

        describe "Using section.reachable to determine if section can be reached":
            it "raises Http404 if it can't be reached":
                self.fake_reachable.expects_call().with_args(self.request).returns(False)
                with self.assertRaises(Http404):
                    self.section.make_view(self.view, self.section)(self.request)

            it "calls view if it can be reached and returns view result":
                self.fake_reachable.expects_call().with_args(self.request).returns(True)
                ret = self.section.make_view(self.view, self.section)(self.request, 1, 2, d=True, c=False) 
                ret |should| be(self.view_result)
    
    describe "Patterns":
        before_each:
            self.fake_make_view = fudge.Fake("make_view")
            self.section = type("Section", (Section, ), {'make_view' : self.fake_make_view})()

        describe "Getting expanded list":
            @fudge.patch("src.sections.section.patterns", "src.sections.section.PatternList")
            it "uses a PatternList object with django patterns generator and wraps view with function that adds section to request", fake_patterns, fakePatternList:
                infos = {}
                patterns = []
                final_results = []

                for i in range(3):
                    info = infos[i] = {}

                    info['name'] = fudge.Fake("name_%d % i")
                    info['kwarg'] = fudge.Fake("kwarg_%d" % i)
                    info['pattern'] = fudge.Fake("pattern_%d" % i)
                    info['section'] = fudge.Fake("section_%d" % i)
                    info['view_result'] = fudge.Fake("view_result_%d" % i)

                    # The view is wrapped before going into the tuple
                    info['view'] = fudge.Fake("view")
                    info['wrapped_view'] = fudge.Fake("wrapped_view")
                    if i == 0:
                        next_call = self.fake_make_view.expects_call()
                    else:
                        next_call = self.fake_make_view.next_call()
                    next_call.with_args(info['view'], info['section']).returns(info['wrapped_view'])

                    # Original tuple to go into section.patterns()
                    # And modified tuple to go into django patterns()
                    info['tuple'] = (info['pattern'], info['view'], info['kwarg'], info['name'])
                    info['modified_tuple'] = (info['pattern'], info['wrapped_view'], info['kwarg'], info['name'])

                    info['result'] = fudge.Fake("result_%d" % i)
                    info['patterns_result'] = [info['result']] 

                    patterns.append((info['section'], info['tuple']))
                    final_results.append(info['result'])

                fakePatternList.expects_call().with_args(self.section).returns(patterns)
                (fake_patterns.expects_call()
                    .with_args('', infos[0]['modified_tuple']).returns(infos[0]['patterns_result'])
                    .next_call().with_args('', infos[1]['modified_tuple']).returns(infos[1]['patterns_result'])
                    .next_call().with_args('', infos[2]['modified_tuple']).returns(infos[2]['patterns_result'])
                    )
                self.section.patterns() |should| equal_to(final_results)

        describe "Getting as includes":
            before_each:
                self.app_name = fudge.Fake("app_name")
                self.namespace = fudge.Fake("namespace")
                self.fake_patterns = fudge.Fake("patterns")
                self.section = type("Section", (Section, ), {'patterns' : self.fake_patterns})()

            @fudge.patch("src.sections.section.include", "src.sections.section.PatternList")
            it "returns include_path from PatternList as first item in tuple", fake_include, fakePatternList:
                end = fudge.Fake("end")
                path = fudge.Fake("path")
                start = fudge.Fake("start")
                include_as = fudge.Fake("include_as")

                # Make fake PatternList instance
                pattern_list = (fudge.Fake("pattern_list").expects("include_path")
                    .with_args(include_as, start, end).returns(path)
                    )
                fakePatternList.expects_call().with_args(self.section).returns(pattern_list)

                # Patterns are for the includer
                self.fake_patterns.expects_call()

                fake_include.expects_call()
                p, _ = self.section.include_patterns(self.namespace, self.app_name
                    , include_as=include_as, start=start, end=end
                    )

                # Make sure we got the path returned from PatternList
                p |should| be(path)

            @fudge.patch("src.sections.section.include", "src.sections.section.PatternList")
            it "returns includer function using django include generator as second item in tuple", fake_include, fakePatternList:
                patterns = fudge.Fake("patterns")
                includer = fudge.Fake("includer")

                # include_path gets path for first item of returned tuple
                pattern_list = fudge.Fake("pattern_list").expects("include_path")
                fakePatternList.expects_call().with_args(self.section).returns(pattern_list)

                # Patterns are passed into include
                self.fake_patterns.expects_call().returns(patterns)

                # includer generates the includer
                fake_include.expects_call().with_args(patterns, self.namespace, self.app_name).returns(includer)
                _, i = self.section.include_patterns(self.namespace, self.app_name)

                # Make sure we got the includer function
                i |should| be(includer)
    
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
            
        @fudge.test
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
            
        @fudge.test
        it "creates a clone of options for the new section":
            section = Section()
            new_options = fudge.Fake("new_options")
            fake_options = fudge.Fake("options").expects("clone").with_args(all=True).returns(new_options)
            section.options = fake_options
            section.clone().options |should| be(new_options)
            
        @fudge.test
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
