# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should, should_not
from django.test import TestCase

from cwf.views.rendering import Renderer
from cwf.views.base import View

import fudge

# Make the errors go away
be, equal_to, respond_to = None, None, None

describe TestCase, "View":
    before_each:
        self.view = View()

    it "sets renderer to an instance of the Renderer":
        type(self.view.renderer) |should| be(Renderer)

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

            self.view(request, target, a, b, c=c, d=d) |should| be(rendered)

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
            for result in (0, 1, True, False, [], [1], [1, 2, 3], (), (1), (1, 2, 3), lambda:True, fudge.Fake("obj")):
                self.view.rendered_from_result(self.request, result) |should| be(result)

        @fudge.test
        it "Returns extra if template is None from template, extra = result":
            extra = fudge.Fake("extra")
            result = (None, extra)
            self.view.rendered_from_result(self.request, result) |should| be(extra)

        @fudge.test
        it "renders template and extra when template,extra = result":
            extra = fudge.Fake("extra")
            result = fudge.Fake("result")
            template = fudge.Fake("template")

            self.renderer.expects("render").with_args(self.request, template, extra).returns(result)
            self.view.rendered_from_result(self.request, (template, extra)) |should| be(result)

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
            ret |should| be(result)

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
            ret |should| be(result)

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
            ret |should| be(final)

        @fudge.test
        it "gets result from execute and returns it if not callable":
            result = type("result", (object, ), {})()
            (self.fake_execute.expects_call()
                .with_args(self.target, self.request, self.args, self.kwargs).returns(result)
                )

            # Has the target
            self.fake_has_target.expects_call().with_args(self.target).returns(True)

            ret = self.view.get_result(self.request, self.target, self.args, self.kwargs)
            ret |should| be(result)

    describe "Determining if view has a target":
        before_each:
            self.target_name = 'the_target_for_great_good'

        it "says False if target isn't an attribute on the class":
            assert not hasattr(self.view, self.target_name)
            self.view.has_target(self.target_name) |should| be(False)

        it "says True if target is an attribute on the class":
            view = type("view", (View, ), {self.target_name: fudge.Fake("target")})()

            assert hasattr(view, self.target_name)
            view.has_target(self.target_name) |should| be(True)

    describe "Getting target from a view":
        before_each:
            self.target_name = 'the_target_for_great_good'

        it "gets target as attribute on the class":
            target = fudge.Fake("target")
            view = type("view", (View, ), {self.target_name : target})()
            view.get_target(self.target_name) |should| be(target)

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
                kwargs[key] |should| be(original)
                return {
                      'a' : cleaned_a
                    , 'b' : cleaned_b
                    , 'c' : cleaned_c
                }[key]

            self.fake_clean_view_kwarg.expects_call().calls(cleaner)
            self.view.clean_view_kwargs(kwargs) |should| be(kwargs)
            kwargs |should| equal_to(dict(a=cleaned_a, b=cleaned_b, c=cleaned_c))

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
                self.view.clean_view_kwarg(key, original) |should| equal_to(cleaned)

        it "item is not a string, it is left alone":
            key = fudge.Fake("key")
            spec = [0, 1, None, True, False, (), (1, ), [], [1], {}, {1:2}, fudge.Fake("obj"), lambda : True]
            for original in spec:
                self.view.clean_view_kwarg(key, original) |should| be(original)

    describe "getting state":
        before_each:
            self.menu = fudge.Fake("menu")
            self.target = fudge.Fake("target")
            self.request = fudge.Fake("request")
            self.section = fudge.Fake("section")
            self.base_url = fudge.Fake("base_url")

            self.fake_get_section = fudge.Fake("get_section")
            self.fake_path_from_request = fudge.Fake("path_from_request")
            self.fake_base_url_from_request = fudge.Fake("request_from_url")

            self.view = type("view", (View, )
                , { 'get_section' : self.fake_get_section
                  , 'path_from_request' : self.fake_path_from_request
                  , 'base_url_from_request' : self.fake_base_url_from_request
                  }
                )()

        @fudge.patch("cwf.views.base.Menu", "cwf.views.base.DictObj")
        it "returns a dictobj with menu, path, target, section and base_url", fakeMenu, fakeDictObj:
            path = fudge.Fake("path")
            result = fudge.Fake("result")
            fakeMenu.expects_call().with_args(self.request, self.section).returns(self.menu)

            self.fake_get_section.expects_call().with_args(self.request, path).returns(self.section)
            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns('')

            (fakeDictObj.expects_call()
                .with_args(menu=self.menu, target=self.target, section=self.section, path=path, base_url='').returns(result)
                )

            self.view.get_state(self.request, self.target) |should| be(result)

        @fudge.patch("cwf.views.base.Menu", "cwf.views.base.DictObj")
        it "doesn't make a menu if can't get a section", fakeMenu, fakeDictObj:
            path = fudge.Fake("path")
            result = fudge.Fake("result")

            self.fake_get_section.expects_call().with_args(self.request, path).returns(None)
            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns('')

            (fakeDictObj.expects_call()
                .with_args(menu=None, target=self.target, section=None, path=path, base_url='').returns(result)
                )

            self.view.get_state(self.request, self.target) |should| be(result)

        @fudge.patch("cwf.views.base.Menu", "cwf.views.base.DictObj")
        it "pops start of path if base url isn't an empty string and path starts with ''", fakeMenu, fakeDictObj:
            path = ['', 'asdf', 'weouri']
            result = fudge.Fake("result")
            fakeMenu.expects_call().with_args(self.request, self.section).returns(self.menu)

            self.fake_get_section.expects_call().with_args(self.request, path).returns(self.section)
            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns(self.base_url)

            (fakeDictObj.expects_call()
                .with_args(
                      menu=self.menu, target=self.target, section=self.section
                    , path=['asdf', 'weouri'], base_url=self.base_url
                    ).returns(result)
                )

            self.view.get_state(self.request, self.target) |should| be(result)

        @fudge.patch("cwf.views.base.Menu", "cwf.views.base.DictObj")
        it "doesn't pop start of path if base url isn't an empty string but path doesn't start with ''", fakeMenu, fakeDictObj:
            path = ['asdf', 'weouri']
            result = fudge.Fake("result")
            fakeMenu.expects_call().with_args(self.request, self.section).returns(self.menu)

            self.fake_get_section.expects_call().with_args(self.request, path).returns(self.section)
            self.fake_path_from_request.expects_call().with_args(self.request).returns(path)
            self.fake_base_url_from_request.expects_call().with_args(self.request).returns(self.base_url)

            (fakeDictObj.expects_call()
                .with_args(
                      menu=self.menu, target=self.target, section=self.section
                    , path=['asdf', 'weouri'], base_url=self.base_url
                    ).returns(result)
                )

            self.view.get_state(self.request, self.target) |should| be(result)

    describe "Getting the current section":
        before_each:
            self.path = fudge.Fake("path")
            self.request = fudge.Fake("request")
            self.section = fudge.Fake("section")

        it "returns the section attribute on the request":
            self.request.has_attr(section=self.section)
            self.view.get_section(self.request, self.path) |should| be(self.section)

        it "returns None if the request has no section":
            self.request |should_not| respond_to('section')
            self.view.get_section(self.request, self.path) |should| be(None)

    describe "getting base url from a request":
        before_each:
            self.meta = {}
            self.request = fudge.Fake("request")

        it "returns empty string if request.META has not SCRIPT_NAME":
            assert 'SCRIPT_NAME' not in self.meta

            self.request.has_attr(META=self.meta)
            self.view.base_url_from_request(self.request) |should| equal_to('')

        it "returns request.META['SCRIPT_NAME']":
            script_name = fudge.Fake("script_name")
            self.meta['SCRIPT_NAME'] = script_name

            self.request.has_attr(META=self.meta)
            self.view.base_url_from_request(self.request) |should| equal_to(script_name)

    describe "Getting path from request":
        before_each:
            self.request = fudge.Fake("request")

        it "ensures request.path has leading and trailing slash and splits by slash":
            specs = [
                  ('a', ['', 'a', ''])
                , ('/a/', ['', 'a', ''])
                , ('/a/b', ['', 'a', 'b', ''])
                , ('/a/b/', ['', 'a', 'b', ''])
                , ('/a/b/c', ['', 'a', 'b', 'c', ''])
                , ('/a/b/c/', ['', 'a', 'b', 'c', ''])

                , ('a', ['', 'a', ''])
                , ('/////a///', ['', 'a', ''])
                , ('/a////b', ['', 'a', 'b', ''])
                , ('////a////b/', ['', 'a', 'b', ''])
                , ('///a/b/////c', ['', 'a', 'b', 'c', ''])
                , ('/a/////b/c////', ['', 'a', 'b', 'c', ''])
                ]

            for original, expected in specs:
                self.request.has_attr(path=original)
                self.view.path_from_request(self.request) |should| equal_to(expected)
