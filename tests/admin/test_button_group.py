# coding: spec

from src.admin.buttons import ButtonGroup

import fudge

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

    describe "Copying for request":
        @fudge.patch("src.admin.buttons.ButtonGroup")
        it "returns a group with same name and copied buttons", fakeButtonGroup:
            copied1 = fudge.Fake("copied1")
            copied2 = fudge.Fake("copied2")
            self.button1.expects("copy_for_request").with_args(self.request, self.original).returns(copied1)
            self.button2.expects("copy_for_request").with_args(self.request, self.original).returns(copied2)

            group = fudge.Fake("group")
            fakeButtonGroup.expects_call().with_args(self.name, [copied1, copied2]).returns(group)
            self.group.copy_for_request(self.request, original=self.original) |should| be(group)
