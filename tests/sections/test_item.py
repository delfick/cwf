# coding: spec

from cwf.sections.section import Item

import fudge

describe "Item":
    before_each:
        self.section = fudge.Fake('section')
        self.include_as = fudge.Fake('include_as')
        self.consider_for_menu = fudge.Fake('consider_for_menu')
        self.item = Item(self.section, self.consider_for_menu, self.include_as)

    it "takes in section, consider_for_menu and include_as":
        self.item.section |should| be(self.section)
        self.item.include_as |should| be(self.include_as)
        self.item.consider_for_menu |should| be(self.consider_for_menu)

    describe "Creating item":
        it "creates an item with the section and only consider_for_menu and include_as from the kwargs":
            options = dict(consider_for_menu=self.consider_for_menu, include_as=self.include_as, a=1, b=2)
            item = fudge.Fake("item")
            fakeItem = (fudge.Fake("Item").expects_call()
                .with_args(self.section, consider_for_menu=self.consider_for_menu, include_as=self.include_as).returns(item)
                )
            Item.create.im_func(fakeItem, self.section, options) |should| be(item)

    describe "Creating clone":
        it "clones the section, merges clone with old section and returns new Item with it":
            parent = fudge.Fake("parent")
            cloned_section = (fudge.Fake("cloned_section")
                .expects("merge").with_args(self.section, take_base=True)
                )
            self.section.expects("clone").with_args(parent=parent).returns(cloned_section)

            item = self.item.clone(parent=parent)
            item.section |should| be(cloned_section)
            item.include_as |should| be(self.include_as)
            item.consider_for_menu |should| be(self.consider_for_menu)
