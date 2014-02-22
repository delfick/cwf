# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should, should_not
from django.test import TestCase

from cwf.admin.admin import ButtonAdminMixin
from cwf.admin.buttons import Button

import fudge

# Make the errors go away
be, respond_to, equal_to = None, None, None

describe TestCase, "ButtonAdminMixin":
    before_each:
        self.model = fudge.Fake("model")
        self.mixin = ButtonAdminMixin()

    describe "Getting button urls":
        @fudge.patch("cwf.admin.admin.ButtonPatterns")
        it "Makes ButtonPatterns object and returns it's patterns", fakeButtonPatterns:
            model = fudge.Fake("model")
            buttons = fudge.Fake("buttons")
            patterns = fudge.Fake("patterns")
            admin_view = fudge.Fake("admin_view")
            admin_site = fudge.Fake("admin_site").has_attr(admin_view=admin_view)
            button_view = fudge.Fake("button_view")
            button_patterns = fudge.Fake("button_patterns").has_attr(patterns=patterns)

            # We create a ButtonPatterns object to do all the logic
            (fakeButtonPatterns.expects_call()
                .with_args(buttons, model, admin_view, button_view).returns(button_patterns)
                )

            # Mixin has all the things we give to the ButtonPatterns object
            self.mixin.model = model
            self.mixin.buttons = buttons
            self.mixin.admin_site = admin_site
            self.mixin.button_view = button_view
            self.mixin.button_urls() |should| be(patterns)

    describe "button view":
        before_each:
            self.extra = fudge.Fake("extra")
            self.result = fudge.Fake("result")
            self.button = fudge.Fake("button")
            self.request = fudge.Fake("request")
            self.template = fudge.Fake("template")
            self.object_id = fudge.Fake("object_id")

            self.fake_button_result = fudge.Fake("button_result")
            self.fake_button_view_context = fudge.Fake("button_view_context")

            self.mixin = type("mixin", (ButtonAdminMixin, )
                , { 'model' : self.model
                  , 'button_result' : self.fake_button_result
                  , 'button_view_context' : self.fake_button_view_context
                  }
                )()

        describe "When we have an object to pass on":
            @fudge.patch("cwf.admin.admin.get_object_or_404", "cwf.admin.admin.renderer")
            it "returns result as is from button_result if not a two item tuple", fake_get_object_or_404, fake_renderer:
                obj = fudge.Fake("object")
                fake_get_object_or_404.expects_call().with_args(self.model, pk=self.object_id).returns(obj)

                self.button.has_attr(for_all=False)
                self.fake_button_result.expects_call().with_args(self.request, obj, self.button).returns(self.result)
                self.mixin.button_view(self.request, self.object_id, self.button) |should| be(self.result)

            @fudge.patch("cwf.admin.admin.get_object_or_404", "cwf.admin.admin.renderer")
            it "doesn't look for an obj if the button is for all", fake_get_object_or_404, fake_renderer:
                self.button.has_attr(for_all = True)
                self.fake_button_result.expects_call().with_args(self.request, None, self.button).returns(self.result)
                self.mixin.button_view(self.request, self.object_id, self.button) |should| be(self.result)

            @fudge.patch("cwf.admin.admin.get_object_or_404", "cwf.admin.admin.renderer")
            it "renders template, extra from result if two item tuple", fake_get_object_or_404, fake_renderer:
                obj = fudge.Fake("object")
                ctxt = fudge.Fake("ctxt")
                render = fudge.Fake("render")

                fake_get_object_or_404.expects_call().with_args(self.model, pk=self.object_id).returns(obj)

                # Button_view_context combines context from button and extra
                self.fake_button_view_context.expects_call().with_args(obj, self.button, self.extra).returns(ctxt)

                # Get back (template, extra) from button result
                (self.fake_button_result.expects_call()
                    .with_args(self.request, obj, self.button).returns((self.template, self.extra))
                    )

                # Render the request with the template and the ctxt we constructed
                self.button.has_attr(for_all=False)
                fake_renderer.expects("render").with_args(self.request, self.template, ctxt).returns(render)
                self.mixin.button_view(self.request, self.object_id, self.button) |should| be(render)

    describe "Getting result from a button":
        before_each:
            self.obj = fudge.Fake("obj")
            self.button = fudge.Fake("button")
            self.request = fudge.Fake("request")

        @fudge.test
        it "delegates to tool_<button_url>":
            url = fudge.Fake("url")
            result = fudge.Fake("result")
            self.button.has_attr(url=url, return_to_form=False)
            delegate = fudge.Fake("delegate").expects_call().with_args(self.request, self.obj, self.button).returns(result)

            name = "tool_%s" % url
            setattr(self.mixin, name, delegate)
            self.mixin.button_result(self.request, self.obj, self.button) |should| be(result)

        @fudge.test
        it "complains if it can't find a delegate":
            url = fudge.Fake("url")
            result = fudge.Fake("result")
            self.button.has_attr(url=url, return_to_form=False)

            name = "tool_%s" % url
            with self.assertRaisesRegexp(Exception, "doesn't have a function for %s" % name):
                self.mixin.button_result(self.request, self.obj, self.button) |should| be(result)

        describe "When button has return_to_form set":
            @fudge.patch("cwf.admin.admin.AdminView", "cwf.admin.admin.renderer")
            it "returns back to the change_form if not for_all and should return_to_form", fakeAdminView, fake_renderer:
                url = fudge.Fake("url")
                btn_url = fudge.Fake("btn_url")

                result = fudge.Fake("result")
                redirect = fudge.Fake("redirect")

                # We expect the delegate on the admin to get called somewhere
                self.button.has_attr(url=btn_url, for_all=False, return_to_form=True)
                delegate = (fudge.Fake("delegate").has_attr(__name__="delegate")
                    .expects_call().with_args(self.request, self.obj, self.button).returns(result)
                    )

                # We expect to get redirected
                fakeAdminView.expects("change_view").with_args(self.obj).returns(url)
                fake_renderer.expects("redirect").with_args(self.request, url, no_processing=True).returns(redirect)

                # Put our delegate on the class
                name = "tool_{}".format(btn_url)
                setattr(self.mixin, name, delegate)

                self.mixin.button_result(self.request, self.obj, self.button) |should| be(redirect)

            @fudge.patch("cwf.admin.admin.AdminView", "cwf.admin.admin.renderer")
            it "returns back to the change_list if for_all and should return_to_form", fakeAdminView, fake_renderer:
                url = fudge.Fake("url")
                btn_url = fudge.Fake("btn_url")

                result = fudge.Fake("result")
                redirect = fudge.Fake("redirect")

                # We expect the delegate on the admin to get called somewhere
                self.button.has_attr(url=btn_url, for_all=True, return_to_form=True)
                delegate = (fudge.Fake("delegate").has_attr(__name__="delegate")
                    .expects_call().with_args(self.request, self.obj, self.button).returns(result)
                    )

                # We expect to get redirected
                fakeAdminView.expects("change_list").with_args(self.model).returns(url)
                fake_renderer.expects("redirect").with_args(self.request, url, no_processing=True).returns(redirect)

                # Put our delegate on the class
                name = "tool_{}".format(btn_url)
                setattr(self.mixin, name, delegate)

                self.mixin.model = self.model
                self.mixin.button_result(self.request, self.obj, self.button) |should| be(redirect)

        describe "Adding buttons to the context of a respons":
            before_each:
                self.request = fudge.Fake("request")
                self.response = fudge.Fake("response")

            it "does nothing if admin has no buttons or empty buttons":
                self.mixin |should_not| respond_to("buttons")
                self.mixin.button_response_context(self.request, self.response)
                self.response |should_not| respond_to("context_data")

                self.mixin.buttons = []
                self.mixin.button_response_context(self.request, self.response)
                self.response |should_not| respond_to("context_data")

                self.mixin.buttons = None
                self.mixin.button_response_context(self.request, self.response)
                self.response |should_not| respond_to("context_data")

            it "gives context_data to response if it doesn't already have it":
                self.mixin.buttons = [Button(1, 1)]
                self.response |should_not| respond_to("context_data")
                self.mixin.button_response_context(self.request, self.response)
                type(self.response.context_data) |should| be(dict)
                self.response.context_data.keys() |should| equal_to(["buttons"])

            it "uses context_data on response if it already has it":
                self.mixin.buttons = [Button(1, 1)]
                self.response.context_data = {'a':1, 'b':2}

                self.mixin.button_response_context(self.request, self.response)
                type(self.response.context_data) |should| be(dict)
                sorted(self.response.context_data.keys()) |should| equal_to(sorted(['a', 'b', "buttons"]))

            @fudge.test
            it "creates a copy of each button for the context":
                button1 = fudge.Fake("button1")
                button2 = fudge.Fake("button2")
                copied1 = fudge.Fake("copied1")
                copied2 = fudge.Fake("copied2")
                original = fudge.Fake("original")

                button1.expects("copy_for_request").with_args(self.request, original).returns(copied1)
                button2.expects("copy_for_request").with_args(self.request, original).returns(copied2)

                self.mixin.buttons = [button1, button2]
                self.response.context_data = {'original' : original}
                self.mixin.button_response_context(self.request, self.response)
                self.response.context_data['buttons'] |should| equal_to([copied1, copied2])
