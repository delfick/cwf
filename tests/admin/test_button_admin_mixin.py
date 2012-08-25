# coding: spec

from src.admin.admin import ButtonAdminMixin
from src.admin.buttons import Button

import fudge

describe "ButtonAdminMixin":
    before_each:
        self.model = fudge.Fake("model")
        self.mixin = ButtonAdminMixin()

    describe "Getting button urls":
        @fudge.patch("src.admin.admin.ButtonPatterns")
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
            @fudge.patch("src.admin.admin.get_object_or_404", "src.admin.admin.renderer")
            it "returns result as is from button_result if not a two item tuple", fake_get_object_or_404, fake_renderer:
                obj = fudge.Fake("object")
                fake_get_object_or_404.expects_call().with_args(self.model, pk=self.object_id).returns(obj)

                self.fake_button_result.expects_call().with_args(self.request, obj, self.button).returns(self.result)
                self.mixin.button_view(self.request, self.object_id, self.button) |should| be(self.result)

            @fudge.patch("src.admin.admin.get_object_or_404", "src.admin.admin.renderer")
            it "renders template, extra from result if two item tuple", fake_get_object_or_404, fake_renderer:
                obj = fudge.Fake("object")
                ctxt = fudge.Fake("ctxt")
                render = fudge.Fake("render")
                
                fake_get_object_or_404.expects_call().with_args(self.model, pk=self.object_id).returns(obj)

                # Button_view_context combines context from button and extra
                self.fake_button_view_context.expects_call().with_args(self.button, self.extra).returns(ctxt)

                # Get back (template, extra) from button result
                (self.fake_button_result.expects_call()
                    .with_args(self.request, obj, self.button).returns((self.template, self.extra))
                    )

                # Render the request with the template and the ctxt we constructed
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
            self.button.has_attr(url=url, execute_and_redirect=False)
            delegate = fudge.Fake("delegate").expects_call().with_args(self.request, self.obj, self.button).returns(result)

            name = "tool_%s" % url
            setattr(self.mixin, name, delegate)
            self.mixin.button_result(self.request, self.obj, self.button) |should| be(result)

        @fudge.test
        it "complains if it can't find a delegate":
            url = fudge.Fake("url")
            result = fudge.Fake("result")
            self.button.has_attr(url=url, execute_and_redirect=False)

            name = "tool_%s" % url
            with self.assertRaisesRegexp(Exception, "doesn't have a function for %s" % name):
                self.mixin.button_result(self.request, self.obj, self.button) |should| be(result)
        
        describe "When button has execute_and_redirect set":
            @fudge.test
            it "finds delegate from button.execute_and_redirect and complains if admin doesn't have that attribute":
                self.button.has_attr(execute_and_redirect='func_to_execute')
                self.obj |should_not| respond_to("func_to_execute")
                with self.assertRaisesRegexp(Exception, "doesn't have a function for func_to_execute"):
                    self.mixin.button_result(self.request, self.obj, self.button)

            @fudge.patch("src.admin.admin.AdminView", "src.admin.admin.renderer")
            it "finds delegate from button.execute_and_redirect and redirects to change_view after executing it", fakeAdminView, fake_renderer:
                func_to_execute = fudge.Fake("func_to_execute").expects_call()
                self.button.has_attr(execute_and_redirect='func_to_execute')
                self.obj.func_to_execute = func_to_execute

                url = fudge.Fake("url")
                result = fudge.Fake("result")
                fakeAdminView.expects("change_view").with_args(self.obj).returns(url)
                fake_renderer.expects("redirect").with_args(url, no_processing=True).returns(result)

                self.mixin.button_result(self.request, self.obj, self.button) |should| be(result)

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
