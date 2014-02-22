# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should
from django.test import TestCase

from cwf.admin.buttons import Button, ButtonGroup
from cwf.admin.admin import ButtonPatterns

from fudge.inspector import arg as fudge_arg
import fudge
import re

# Make the errors go away
be, equal_to = None, None

describe TestCase, "Button Patterns":
    before_each:
        self.model = fudge.Fake("model")
        self.buttons = fudge.Fake("buttons")
        self.admin_view = fudge.Fake("admin_view")
        self.button_view = fudge.Fake("button_view")

        self.patterns = ButtonPatterns(self.buttons, self.model, self.admin_view, self.button_view)

    it "takes in buttons, model, admin_view and button_view":
        self.patterns.model |should| be(self.model)
        self.patterns.buttons |should| be(self.buttons)
        self.patterns.admin_view |should| be(self.admin_view)
        self.patterns.button_view |should| be(self.button_view)

    describe "getting patterns":
        before_each:
            self.fake_iter_buttons = fudge.Fake("iter_buttons")
            self.fake_button_pattern = fudge.Fake("button_Pattern")
            self.patterns = type("patterns", (ButtonPatterns, )
                , { 'iter_buttons' : self.fake_iter_buttons
                  , 'button_pattern' : self.fake_button_pattern
                  }
                )(self.buttons, self.model, self.admin_view, self.button_view)

        @fudge.patch("cwf.admin.admin.patterns")
        it "Returns django patterns object from creating a button for each button", fake_patterns:
            b1 = fudge.Fake("b1")
            b2 = fudge.Fake("b2")
            b3 = fudge.Fake("b3")
            bp1 = fudge.Fake("bp1")
            bp2 = fudge.Fake("bp2")
            bp3 = fudge.Fake("bp3")

            # iter_buttons provides the buttons we care about
            self.fake_iter_buttons.expects_call().returns([b1, b2, b3])

            # Button pattern returns us a pattern for each button
            def button_pattern(button):
                return {
                      b1 : bp1
                    , b2 : bp2
                    , b3 : bp3
                    }[button]
            self.fake_button_pattern.expects_call().calls(button_pattern)

            # All button patterns are passed into the patterns function
            result = fudge.Fake("result")
            (fake_patterns.expects_call()
                .with_args('', bp1, bp2, bp3).returns(result)
                )

            # Result of patterns is returned
            self.patterns.patterns |should| be(result)

    describe "Itering buttons":
        before_each:
            self.buttons = []
            for button in range(10):
                self.buttons.append(Button("%s_name" % button, "%s_desc" % button))

        it "Yields each button in self.buttons":
            patterns = ButtonPatterns(self.buttons, self.model, self.admin_view, self.button_view)
            list(patterns.iter_buttons()) |should| equal_to(self.buttons)

        it "Recurses into Button Groups":
            buttons = [self.buttons[0], self.buttons[1], self.buttons[2]]
            button_group1 = ButtonGroup("bg1", [self.buttons[9], self.buttons[8]])
            button_group2 = ButtonGroup("bg2", [self.buttons[6], self.buttons[5], button_group1])
            buttons.append(button_group2)

            patterns = ButtonPatterns(buttons, self.model, self.admin_view, self.button_view)
            expected = [self.buttons[index] for index in (0, 1, 2, 6, 5, 9, 8)]
            list(patterns.iter_buttons()) |should| equal_to(expected)

    describe "Getting url for a button":
        it "returns anything followed by tool_url/":
            button = fudge.Fake("button").has_attr(for_all=False, url='bob')
            pattern = self.patterns.button_url(button)

            pattern |should| equal_to(r'^(.+)/tool_bob/$')
            compiled = re.compile(pattern)

            assert     compiled.match("alskjlkj/asdfasdf/tool_bob/")
            assert not compiled.match("alskjlkj/asdfasdf/tool_bob")
            assert not compiled.match("alskjlkj/asdfasdf/tool_bob/adfasf")

        it "returns just by tool_url/ if for_all":
            button = fudge.Fake("button").has_attr(for_all=True, url='bob')
            pattern = self.patterns.button_url(button)

            pattern |should| equal_to(r'^tool_bob/$')
            compiled = re.compile(pattern)

            assert     compiled.match("tool_bob/")
            assert not compiled.match("alskjlkj/tool_bob")
            assert not compiled.match("tool_bob/adfasf")

    describe "Getting name for the button view":
        it "uses app label and module_name from the model and url from the button":
            app_label = fudge.Fake("app_label")
            module_name = fudge.Fake("module_name")

            button_url = fudge.Fake("button_url")
            button = fudge.Fake("button").has_attr(url=button_url)

            meta = fudge.Fake("meta").has_attr(app_label=app_label, module_name=module_name)
            self.model.has_attr(_meta=meta)

            expected = '%s_%s_tool_%s' % (app_label, module_name, button_url)
            self.patterns.button_name(button) |should| equal_to(expected)

    describe "Getting function for button view":
        @fudge.patch("cwf.admin.admin.wraps")
        it "Creates a function that pretends to be self.button_view but wraps view in admin_view", fake_wraps:
            a = fudge.Fake("a")
            b = fudge.Fake("b")
            c = fudge.Fake("c")
            d = fudge.Fake("d")
            result = fudge.Fake("result")
            final_wrapped = fudge.Fake("final_wrapped")

            # Wraps makes the returned function pretend to be button_view
            def pretend_to_wrap(view):
                """Pretend to call wraps"""
                def wrapped(func):
                    """Our wrapper just returns the function it was given"""
                    return func
                return wrapped
            fake_wraps.expects_call().with_args(self.button_view).calls(pretend_to_wrap)

            # Admin_view gets called with button_view to produce something that is called
            self.admin_view.expects_call().with_args(self.button_view).returns(final_wrapped)

            # We expect final_wrapped to be called with particular args and kwargs
            final_wrapped.expects_call().with_args(a, b, c=c, d=d).returns(result)

            # Should get back button_func from updating wrapper with button_view
            # and calling it should eventually get to our final_wrapped and get us the result
            self.patterns.button_func()(a, b, c=c, d=d) |should| be(result)

    describe "Getting pattern for the button":
        before_each:
            self.fake_button_url = fudge.Fake("button_url")
            self.fake_button_name = fudge.Fake("button_name")
            self.fake_button_func = fudge.Fake("button_func")
            self.patterns = type("patterns", (ButtonPatterns, )
                , { 'button_url' : self.fake_button_url
                  , 'button_name' : self.fake_button_name
                  , 'button_func' : self.fake_button_func
                  }
                )(self.buttons, self.model, self.admin_view, self.button_view)

        @fudge.patch("cwf.admin.admin.url")
        it "returns url object with location, view, name and kwargs", fake_url:
            loc = fudge.Fake("loc")
            name = fudge.Fake("name")
            view = fudge.Fake("view")
            button = fudge.Fake("button")
            pattern = fudge.Fake("pattern")

            # Get location, name and func from ButtonPatterns object
            self.fake_button_url.expects_call().with_args(button).returns(loc)
            self.fake_button_name.expects_call().with_args(button).returns(name)

            # button_func doesn't need button to be made
            self.fake_button_func.expects_call().returns(view)

            # Make sure the button is passed in as kwargs
            def dict_with_button(kwargs):
                kwargs |should| equal_to(dict(button=button))
                return True

            # All goes into a django url object
            (fake_url.expects_call()
                .with_args(loc, view, name=name, kwargs=fudge_arg.passes_test(dict_with_button)).returns(pattern)
                )

            self.patterns.button_pattern(button) |should| be(pattern)
