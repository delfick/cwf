# coding: spec

from src.admin.admin import ButtonAdmin

import fudge

describe "ButtonAdmin":
    before_each:
        self.meta = fudge.Fake("meta")
        self.model = fudge.Fake("model").has_attr(_meta=self.meta)
        self.admin_site = fudge.Fake('admin_site')

        self.admin = ButtonAdmin(self.model, self.admin_site)

    describe "urls":
        before_each:
            self.fake_get_urls = fudge.Fake("get_urls")
            self.fake_button_urls = fudge.Fake("button_urls")
            self.admin = type("admin", (ButtonAdmin, )
                , { 'get_urls' : self.fake_get_urls
                  , 'button_urls' : self.fake_button_urls
                  }
                )(self.model, self.admin_site)

        @fudge.test
        it "combines button_urls and get_urls if it has buttons":
            buttons = fudge.Fake("buttons")
            button_url = fudge.Fake("button_url")
            normal_url = fudge.Fake("normal_url")

            self.admin.buttons = buttons
            self.fake_get_urls.expects_call().returns([normal_url])
            self.fake_button_urls.expects_call().returns([button_url])

            self.admin.urls |should| equal_to([button_url, normal_url])

        @fudge.test
        it "just returns get_urls if no buttons":
            urls = fudge.Fake("urls")
            self.fake_get_urls.expects_call().returns(urls)
            self.admin |should_not| respond_to("buttons")

            self.admin.urls |should| be(urls)

    describe "Adding buttons to context":
        @fudge.test
        def ensure_context_added(self, method, super_kls):
            """
                Make sure that we override a method such that:
                The original super is called
                And then the response is altered by button_response_context
                Before the response is returned
            """
            a = fudge.Fake('a')
            b = fudge.Fake('b')
            c = fudge.Fake('c')
            d = fudge.Fake('d')
            request = fudge.Fake("request")
            response = fudge.Fake("response")

            fake_button_response_context = (fudge.Fake("button_response_context")
                .expects_call().with_args(request, response)
                )

            admin = type("admin", (ButtonAdmin, )
                , { 'button_response_context' : fake_button_response_context
                  }
                )(self.model, self.admin_site)

            super_object = (fudge.Fake("super").expects(method)
                .with_args(request, a, b, c=c, d=d).returns(response)
                )
            fake_super = fudge.Fake("super").expects_call().returns(super_object)

            with fudge.patched_context("__builtin__", 'super', fake_super):
                getattr(admin, method)(request, a, b, c=c, d=d) |should| be(response)

        it "adds buttons to the changelist_view":
            self.ensure_context_added("changelist_view", "src.admin.admin.admin.ModelAdmin")

        it "adds buttons to the change_form":
            self.ensure_context_added("render_change_form", "src.admin.admin.admin.ModelAdmin")

    describe "Altering response to change":
        before_each:
            self.obj = fudge.Fake("obj")
            self.request = fudge.Fake("request")

        @fudge.patch("src.admin.admin.renderer")
        it "redirects to the key in POST that begins with tool_ if one is there", fake_renderer:
            redirect = fudge.Fake("redirect")
            self.request.POST = {'a':1, "tool_bob" : True}
            fake_renderer.expects("redirect").with_args("tool_bob", no_processing=True).returns(redirect)

            self.admin.response_change(self.request, self.obj) |should| be(redirect)

        @fudge.patch("src.admin.admin.renderer")
        it "returns as normal if no tool_ key is in POST", fake_renderer:
            # Renderer shouldn't be touched in this test
            result = fudge.Fake("result")
            self.request.POST = {}
            super_object = (fudge.Fake("super_object").expects("response_change")
                .with_args(self.request, self.obj).returns(result)
                )
            fake_super = fudge.Fake("super").expects_call().returns(super_object)

            with fudge.patched_context("__builtin__", "super", fake_super):
                self.admin.response_change(self.request, self.obj) |should| be(result)
