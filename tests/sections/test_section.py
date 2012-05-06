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
            it "creates a section with provided url and name, and parent as current section"
            it "gives section a clone of current options with match overriden"
        
        describe "Adopting sections": pass
        describe "Merging in other sections": pass
        describe "Adding a copy of a section": pass
        describe "Adding a section": pass
        
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
