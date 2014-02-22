# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should

from cwf.admin.buttons import ButtonGroup

import fudge

# Make the errors go away
be = None

describe "Button Group":
    before_each:
        self.name = fudge.Fake("name")
        self.request = fudge.Fake("request")
        self.original = fudge.Fake("original")

        self.button1 = fudge.Fake("button1")
        self.button2 = fudge.Fake("button2")
        self.buttons = [self.button1, self.button2]

        self.group = ButtonGroup(self.name, self.buttons)

    it "sets group to True":
        self.group.group |should| be(True)

    it "sets name and buttons onto instance":
        self.group.name |should| be(self.name)
        self.group.buttons |should| be(self.buttons)

    describe "Determining if a group can be shown":
        it "says no if none of the children say yes":
            child1 = fudge.Fake("child1").has_attr(show=False)
            child2 = fudge.Fake("child2").has_attr(show=False)
            child3 = fudge.Fake("child3").has_attr(show=False)
            ButtonGroup(self.name, [child1, child2, child3]).show |should| be(False)

        it "says yes if any of the children say yes":
            child1 = fudge.Fake("child1").has_attr(show=False)
            child2 = fudge.Fake("child2").has_attr(show=True)
            child3 = fudge.Fake("child3").has_attr(show=False)
            ButtonGroup(self.name, [child1, child2, child3]).show |should| be(True)

    describe "Copying for request":
        @fudge.patch("cwf.admin.buttons.ButtonGroup")
        it "returns a group with same name and copied buttons", fakeButtonGroup:
            copied1 = fudge.Fake("copied1")
            copied2 = fudge.Fake("copied2")
            self.button1.expects("copy_for_request").with_args(self.request, self.original).returns(copied1)
            self.button2.expects("copy_for_request").with_args(self.request, self.original).returns(copied2)

            group = fudge.Fake("group")
            fakeButtonGroup.expects_call().with_args(self.name, [copied1, copied2]).returns(group)
            self.group.copy_for_request(self.request, original=self.original) |should| be(group)
