# coding: spec

from src.views.rendering import Renderer
from src.views.base import View

import fudge

describe "View":
    before_each:
        self.view = View()

    it "sets renderer to an instance of the Renderer":
        self.assertIs(type(self.view.renderer), Renderer)

    describe "Calling the view":
        before_each:
            self.fake_get_state = fudge.Fake("get_state")
            self.fake_get_result = fudge.Fake("get_result")
            self.fake_clean_view_kwargs = fudge.Fake("clean_view_kwargs")
            self.fake_rendered_from_result = fudge.Fake("rendered_from_result")

            self.view = type("View", (View, )
                , { "get_state" : self.fake_get_state
                  , "get_result" : self.fake_get_result
                  , "clean_view_kwargs" : self.fake_clean_view_kwargs
                  , "rendered_from_result" : self.fake_rendered_from_result
                  }
                )()

        @fudge.test
        it "sets state on the request, cleans the kwargs and renders the result":
            a = fudge.Fake("a")
            b = fudge.Fake("b")
            c = fudge.Fake("c")
            d = fudge.Fake("d")
            state = fudge.Fake("state")
            target = fudge.Fake("target")
            result = fudge.Fake("result")
            request = fudge.Fake("request")
            rendered = fudge.Fake("rendered")
            cleaned_kwargs = fudge.Fake("cleaned_kwargs")

            self.fake_get_state.expects_call().with_args(request, target).returns(state)
            self.fake_clean_view_kwargs.expects_call().with_args(dict(c=c, d=d)).returns(cleaned_kwargs)
            self.fake_get_result.expects_call().with_args(request, target, (a, b), cleaned_kwargs).returns(result)
            self.fake_rendered_from_result.expects_call().with_args(request, result).returns(rendered)

            self.assertIs(self.view(request, target, a, b, c=c, d=d), rendered)

    describe "rendering a result":
        before_each:
            self.request = fudge.Fake("request")
            self.renderer = fudge.Fake("renderer")
            self.view.renderer = self.renderer

        @fudge.test
        it "raises 404 if passed in result is None":
            Http404 = type("404", (Exception, ), {})
            self.renderer.expects("raise404").raises(Http404)

            with self.assertRaises(Http404):
                self.view.rendered_from_result(self.request, None)

        @fudge.test
        it "returns result as is if not a two item tuple or list":
            for result in (0, 1, True, False, [], [1], [1, 2, 3], (), (1), (1, 2, 3), lambda:true, fudge.Fake("obj")):
                self.assertIs(self.view.rendered_from_result(self.request, result), result)

        @fudge.test
        it "Returns extra if template is None from template, extra = result":
            extra = fudge.Fake("extra")
            result = (None, extra)
            self.assertIs(self.view.rendered_from_result(self.request, result), extra)

        @fudge.test
        it "renders template and extra when template,extra = result":
            extra = fudge.Fake("extra")
            result = fudge.Fake("result")
            template = fudge.Fake("template")

            self.renderer.expects("render").with_args(self.request, template, extra).returns(result)
            self.assertIs(self.view.rendered_from_result(self.request, (template, extra)), result)
