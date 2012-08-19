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

    describe "Executing a target":
        before_each:
            self.target = fudge.Fake("target")
            self.request = fudge.Fake("request")

            self.fake_get_target = fudge.Fake("get_target")
            self.view = type("View", (View, )
                , {'get_target' : self.fake_get_target
                  }
                )()

        @fudge.test
        it "just gets target from the view and executes it":
            a = fudge.Fake("a")
            b = fudge.Fake("b")
            c = fudge.Fake("c")
            d = fudge.Fake("d")
            result = fudge.Fake("result")

            target = (fudge.Fake("target").expects_call()
                .with_args(self.request, a, b, c=c, d=d).returns(result)
                )

            self.fake_get_target.expects_call().with_args(self.target).returns(target)
            ret = self.view.execute(self.target, self.request, [a, b], dict(c=c, d=d))
            self.assertIs(ret, result)

    describe "Getting a result":
        before_each:
            self.args = fudge.Fake("args")
            self.kwargs = fudge.Fake("kwargs")
            self.target = fudge.Fake("target")
            self.request = fudge.Fake("request")

            self.fake_execute = fudge.Fake("execute")
            self.fake_has_target = fudge.Fake("has_target")
            self.view = type("View", (View, )
                , { 'execute' : self.fake_execute
                  , 'has_target' : self.fake_has_target
                  }
                )()

        @fudge.test
        it "uses override if it's defined":
            result = fudge.Fake("result")
            fake_override = (fudge.Fake("override").expects_call()
                .with_args(self.request, self.target, self.args, self.kwargs).returns(result)
                )

            view = type("view", (View, ), {'override' : fake_override})()
            ret = view.get_result(self.request, self.target, self.args, self.kwargs)
            self.assertIs(ret, result)

        @fudge.test
        it "complains if view doesn't have target":
            self.fake_has_target.expects_call().with_args(self.target).returns(False)
            with self.assertRaisesRegexp(Exception, "View object doesn't have a target : %s" % self.target):
                self.view.get_result(self.request, self.target, self.args, self.kwargs)

        @fudge.test
        it "gets result from execute and calls it with request if callable":
            final = fudge.Fake("final")
            result = fudge.Fake("result").expects_call().with_args(self.request).returns(final)
            (self.fake_execute.expects_call()
                .with_args(self.target, self.request, self.args, self.kwargs).returns(result)
                )

            # Has the target
            self.fake_has_target.expects_call().with_args(self.target).returns(True)

            ret = self.view.get_result(self.request, self.target, self.args, self.kwargs)
            self.assertIs(ret, final)

        @fudge.test
        it "gets result from execute and returns it if not callable":
            result = type("result", (object, ), {})()
            (self.fake_execute.expects_call()
                .with_args(self.target, self.request, self.args, self.kwargs).returns(result)
                )

            # Has the target
            self.fake_has_target.expects_call().with_args(self.target).returns(True)

            ret = self.view.get_result(self.request, self.target, self.args, self.kwargs)
            self.assertIs(ret, result)

    describe "Determining if view has a target":
        before_each:
            self.target_name = 'the_target_for_great_good'

        it "says False if target isn't an attribute on the class":
            assert not hasattr(self.view, self.target_name)
            self.assertIs(self.view.has_target(self.target_name), False)

        it "says True if target is an attribute on the class":
            view = type("view", (View, ), {self.target_name: fudge.Fake("target")})()

            assert hasattr(view, self.target_name)
            self.assertIs(view.has_target(self.target_name), True)

    describe "Getting target from a view":
        before_each:
            self.target_name = 'the_target_for_great_good'

        it "gets target as attribute on the class":
            target = fudge.Fake("target")
            view = type("view", (View, ), {self.target_name : target})()
            self.assertIs(view.get_target(self.target_name), target)

    describe "Cleaning view kwargs":
        before_each:
            self.fake_clean_view_kwarg = fudge.Fake("clean_view_kwarg")
            self.view = type("view", (View, )
                , { 'clean_view_kwarg' : self.fake_clean_view_kwarg
                  }
                )()

        @fudge.test
        it "replaces each kwarg with a cleaned version":
            a = fudge.Fake("a")
            b = fudge.Fake("b")
            c = fudge.Fake("c")
            cleaned_a = fudge.Fake("cleaned_a")
            cleaned_b = fudge.Fake("cleaned_b")
            cleaned_c = fudge.Fake("cleaned_c")

            kwargs = dict(a=a, b=b, c=c)
            def cleaner(key, original):
                self.assertIs(kwargs[key], original)
                return {
                      'a' : cleaned_a
                    , 'b' : cleaned_b
                    , 'c' : cleaned_c
                }[key]

            self.fake_clean_view_kwarg.expects_call().calls(cleaner)
            self.assertIs(self.view.clean_view_kwargs(kwargs), kwargs)
            self.assertDictEqual(kwargs, dict(a=cleaned_a, b=cleaned_b, c=cleaned_c))

    describe 'cleaning a single kwarg':
        it "item is a string, it is stripped of leading slashes":
            spec = [
                  ('asdf', 'asdf')
                , ('/asdf', '/asdf')
                , ('//asdf', '//asdf')

                , ('asdf/', 'asdf')
                , ('/asdf/', '/asdf')
                , ('//asdf/', '//asdf')

                , ('asdf//', 'asdf')
                , ('/asdf//', '/asdf')
                , ('//asdf//', '//asdf')
            ]

            key = fudge.Fake("key")
            for original, cleaned in spec:
                self.assertEqual(self.view.clean_view_kwarg(key, original), cleaned)

        it "item is not a string, it is left alone":
            key = fudge.Fake("key")
            spec = [0, 1, None, True, False, (), (1, ), [], [1], {}, {1:2}, fudge.Fake("obj"), lambda : func]
            for original in spec:
                self.assertIs(self.view.clean_view_kwarg(key, original), original)
    

    describe "getting state":
        before_each:
            self.menu = fudge.Fake("menu")
            self.target = fudge.Fake("target")
            self.request = fudge.Fake("request")
            self.base_url = fudge.Fake("base_url")

            self.fake_path_from_request = fudge.Fake("path_from_request")
            self.fake_base_url_from_request = fudge.Fake("request_from_url")

            self.view = type("view", (View, )
                , { 'path_from_request' : self.fake_path_from_request
                  , 'base_url_from_request' : self.fake_base_url_from_request
                  }
                )()

        @fudge.patch("src.views.base.Menu", "src.views.base.DictObj")
        it "returns a dictobj with menu, path, target and base_url", fakeMenu, fakeDictObj:
            path = fudge.Fake("path")
            result = fudge.Fake("result")
            fakeMenu.expects_call().with_args(self.request, path).returns(self.menu)

            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns('')

            (fakeDictObj.expects_call()
                .with_args(menu=self.menu, target=self.target, path=path, base_url='').returns(result)
                )

            self.assertIs(self.view.get_state(self.request, self.target), result)

        @fudge.patch("src.views.base.Menu", "src.views.base.DictObj")
        it "pops start of path if base url isn't an empty string and path starts with ''", fakeMenu, fakeDictObj:
            path = ['', 'asdf', 'weouri']
            result = fudge.Fake("result")
            fakeMenu.expects_call().with_args(self.request, path).returns(self.menu)

            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns(self.base_url)

            (fakeDictObj.expects_call()
                .with_args(
                      menu=self.menu, target=self.target
                    , path=['asdf', 'weouri'], base_url=self.base_url
                    ).returns(result)
                )

            self.assertIs(self.view.get_state(self.request, self.target), result)
        
        @fudge.patch("src.views.base.Menu", "src.views.base.DictObj")
        it "doesn't pop start of path if base url isn't an empty string but path doesn't start with ''", fakeMenu, fakeDictObj:
            path = ['asdf', 'weouri']
            result = fudge.Fake("result")
            fakeMenu.expects_call().with_args(self.request, path).returns(self.menu)

            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns(self.base_url)

            (fakeDictObj.expects_call()
                .with_args(
                      menu=self.menu, target=self.target
                    , path=['asdf', 'weouri'], base_url=self.base_url
                    ).returns(result)
                )

            self.assertIs(self.view.get_state(self.request, self.target), result)
