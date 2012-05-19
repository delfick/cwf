# coding: spec

from src.sections.errors import ConfigurationError
from src.sections.section import Section

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
        it "is lazily loaded"
        it "is created as a type of Options"
    
    describe "Alias":
        it "uses self.options.alias"
        it "uses capitialized url if no options.alias"
    
    describe "Children":
        it "yields self._base first"
        it "yields all other children after base"
        it "ignores base if it isn't defined"
        it "considers base and children as tuples of (item, _)"
    
    describe "menu sections":
        it "yields self._base first"
        it "yields children after self._base"
        it "doesn't yield self._base or children if consider_for_menu is Falsey"
    
    describe "Itering section":
        it "yields self first"
        it "yields all children after self"
    
    describe "Patterns":
        describe "Getting patterns as normal patterns": pass
        describe "Getting patterns as includes": pass
        describe "Getting list of normal patterns": pass
    
    describe "Url creation":
        describe "Getting pattern for url": pass
        describe "Getting path for pattern include": pass
        describe "Getting different parts that make up the url": pass
    
    describe "Cloning": pass
    describe "Getting root ancestor": pass
    describe "Determining if reachable": pass
