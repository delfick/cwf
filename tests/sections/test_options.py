# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should, should_not
from django.test import TestCase

from cwf.sections.errors import ConfigurationError
from cwf.sections.options import Options

from django.http import Http404
import fudge

# Make the errors go away
be, equal_to, throw, be_thrown_by = None, None, None, None

describe TestCase, "Options":
    describe "Getting result of conditional for a request":
        before_each:
            self.result = fudge.Fake("result")
            self.request = fudge.Fake("request")

        it "returns val as is if a boolean":
            options = fudge.Fake("options")
            for val in (False, True):
                options.thing = val
                Options.conditional.im_func(options, 'thing', self.request) |should| be(val)

        @fudge.test
        it "returns result of calling val with request if callable":
            thing = fudge.Fake("thing")
            options = fudge.Fake("options")
            options.thing = thing

            thing.expects_call().with_args(self.request).returns(self.result)
            Options.conditional.im_func(options, 'thing', self.request) |should| be(self.result)

    describe "Determining if options has permission for a request":
        before_each:
            self.user = fudge.Fake("user")
            self.options = Options()

        it "returns True if needsAuth is falsey":
            for val in (False, None, 0):
                self.options.needs_auth = val
                self.options.has_permissions(self.user) |should| be(True)

        @fudge.test
        it "returns whether user.is_authenticated() if needsAuth is True":
            authenticated = fudge.Fake("authenticated")
            self.user.expects("is_authenticated").returns(authenticated)
            self.options.needs_auth = True
            self.options.has_permissions(self.user) |should| be(authenticated)

        @fudge.test
        it "returns True if user.is_authenticated() and user.has_perm(auth) for all auth in needs_auth if a list":
            auth1 = fudge.Fake("auth1")
            auth2 = fudge.Fake("auth2")
            (self.user
                .expects("is_authenticated").returns(True)
                .expects("has_perm")
                    .with_args(auth1).returns(True)
                    .next_call().with_args(auth2).returns(True)
                )

            self.options.needs_auth = [auth1, auth2]
            self.options.has_permissions(self.user) |should| be(True)

        @fudge.test
        it "returns False if not user.is_authenticated() and needs_auth is a list":
            auth1 = fudge.Fake("auth1")
            auth2 = fudge.Fake("auth2")
            (self.user
                .expects("is_authenticated").returns(False)
                )

            self.options.needs_auth = [auth1, auth2]
            self.options.has_permissions(self.user) |should| be(False)

        @fudge.test
        it "returns False if not user.is_authenticated() and needs_auth is not a list":
            needs_auth = fudge.Fake("needs_auth")
            (self.user
                .expects("is_authenticated").returns(False)
                )

            self.options.needs_auth = needs_auth
            self.options.has_permissions(self.user) |should| be(False)

        @fudge.test
        it "returns False if user.is_authenticated() but not user.has_perm(auth) for all auth in needs_auth if a list":
            auth1 = fudge.Fake("auth1")
            auth2 = fudge.Fake("auth2")
            (self.user
                .expects("is_authenticated").returns(True)
                .expects("has_perm")
                    .with_args(auth1).returns(True)
                    .next_call().with_args(auth2).returns(False)
                )

            self.options.needs_auth = [auth1, auth2]
            self.options.has_permissions(self.user) |should| be(False)

        @fudge.test
        it "returns False if user.is_authenticated() but not user.has_perm(needs_auth) if not a list":
            needs_auth = fudge.Fake("needs_auth")
            (self.user
                .expects("is_authenticated").returns(True)
                .expects("has_perm").with_args(needs_auth).returns(False)
                )

            self.options.needs_auth = needs_auth
            self.options.has_permissions(self.user) |should| be(False)

        @fudge.test
        it "returns True if user.is_authenticated() and user.has_perm(needs_auth) if not a list":
            needs_auth = fudge.Fake("needs_auth")
            (self.user
                .expects("is_authenticated").returns(True)
                .expects("has_perm").with_args(needs_auth).returns(True)
                )

            self.options.needs_auth = needs_auth
            self.options.has_permissions(self.user) |should| be(True)

    describe "Determining if options reachable for a request":
        before_each:
            self.user = fudge.Fake("user")
            self.request = fudge.Fake("request")
            self.fake_conditional = fudge.Fake("conditional")
            self.fake_has_permissions = fudge.Fake("has_permissions")

            self.options = type("Options", (Options, )
                , {"conditional" : self.fake_conditional, "has_permissions" : self.fake_has_permissions}
            )()

        @fudge.test
        it "returns False if not conditional(exists)":
            self.fake_conditional.expects_call().with_args('exists', self.request).returns(False)
            self.options.reachable(self.request) |should| be(False)

        @fudge.test
        it "returns False if not conditional(active)":
            (self.fake_conditional.expects_call()
                .with_args('exists', self.request).returns(True)
                .next_call().with_args('active', self.request).returns(False)
                )
            self.options.reachable(self.request) |should| be(False)

        @fudge.test
        it "returns whether self.has_permissions if both exists and active":
            permissions = fudge.Fake("permissions")
            (self.fake_conditional.expects_call()
                .with_args('exists', self.request).returns(True)
                .next_call().with_args('active', self.request).returns(True)
                )

            self.request.user = self.user
            self.fake_has_permissions.expects_call().with_args(self.user).returns(permissions)
            self.options.reachable(self.request) |should| be(permissions)

    describe "Cloning":
        before_each:
            self.options = Options()

        @fudge.test
        it "passes on everything set by the setters if all is True":
            keys = []
            for _, requirements in self.options.setters():
                keys.extend(requirements)

            kwargs = {}
            for requirement in keys:
                next = fudge.Fake(requirement)
                setattr(self.options, requirement, next)
                kwargs[requirement] = next

            cloned = fudge.Fake("cloned").expects("set_everything").with_args(**kwargs)
            fakeOptions = fudge.Fake("Options").expects_call().returns(cloned)
            with fudge.patched_context("cwf.sections.options", "Options", fakeOptions):
                self.options.clone(all=True) |should| be(cloned)

        @fudge.test
        it "passes on everything set by the setters except for alias, match, values, target, propogate_display and promote_children if all is False":
            keys = []
            for _, requirements in self.options.setters():
                keys.extend(requirements)

            kwargs = {}
            for requirement in keys:
                if requirement not in (
                      'alias', 'match', 'values', 'redirect'
                    , 'promote_children', 'target', 'propogate_display'
                    ):
                    next = fudge.Fake(requirement)
                    setattr(self.options, requirement, next)
                    kwargs[requirement] = next

            cloned = fudge.Fake("cloned").expects("set_everything").with_args(**kwargs)
            fakeOptions = fudge.Fake("Options").expects_call().returns(cloned)
            with fudge.patched_context("cwf.sections.options", "Options", fakeOptions):
                self.options.clone(all=False) |should| be(cloned)

        it "original doesn't get affected if clone is modified":
            keys = []
            for _, requirements in self.options.setters():
                keys.extend(requirements)

            original = {}
            for requirement in keys:
                original[requirement] = getattr(self.options, requirement)

            cloned = self.options.clone()
            for requirement in keys:
                getattr(self.options, requirement) |should| be(original[requirement])
                next = fudge.Fake("next")
                setattr(cloned, requirement, next)
                getattr(cloned, requirement) |should| be(next)
                getattr(self.options, requirement) |should| be(original[requirement])

        it "ovverides clone with kwargs":
            keys = []
            for _, requirements in self.options.setters():
                keys.extend(requirements)

            kwargs = {'admin' : fudge.Fake("kls"), 'match' : fudge.Fake("match")}
            original = {}
            for requirement in keys:
                original[requirement] = getattr(self.options, requirement)
                if requirement in kwargs:
                    original[requirement] |should_not| be(kwargs[requirement])

            cloned = self.options.clone(**kwargs)
            for requirement in keys:
                if requirement in kwargs:
                    getattr(cloned, requirement) |should| be(kwargs[requirement])
                else:
                    getattr(cloned, requirement) |should| equal_to(original[requirement])

        it "complains if values in kwargs aren't valid":
            self.options.clone()
            assert True

            admin = lambda one, two, three: 1
            caller = lambda : self.options.clone(admin=admin)
            caller |should| throw(ConfigurationError
                , message="Conditionals as callables must only accept one argument, not 3 (['one', 'two', 'three'])"
                )

        it "doesn't pass on display if propogate_display is False":
            for display in (False, lambda r:1):
                options = Options()
                options.set_everything(display=display, propogate_display=False)
                selective_clone = options.clone()
                selective_clone.display |should_not| be(display)
                selective_clone.propogate_display |should| be(True)

                total_clone = options.clone(all=True)
                total_clone.display |should_not| be(display)
                total_clone.propogate_display |should| be(False)

    describe "Creating patterns":
        before_each:
            self.url_parts = fudge.Fake("url_parts")
            self.fake_string_from_url_parts = fudge.Fake("string_from_url_parts")
            self.options = type("Options", (Options, ), {'string_from_url_parts' : self.fake_string_from_url_parts})()

        @fudge.test
        it "returns '^.*' if string_from_url_parts is None":
            self.fake_string_from_url_parts.expects_call().with_args(self.url_parts).returns(None)
            self.options.create_pattern(self.url_parts) |should| equal_to("^.*/$")

        @fudge.test
        it "returns '^.*' without the dollar sign if no url and catch_all is true":
            self.fake_string_from_url_parts.expects_call().with_args(self.url_parts).returns(None)
            self.options.catch_all = True
            self.options.create_pattern(self.url_parts) |should| equal_to("^.*")

        @fudge.test
        it "returns '^$' if string_from_url_parts is '' or '/'":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns('/')
                .next_call().with_args(self.url_parts).returns('')
                )

            for expected in ('^$', '^$'):
                self.options.create_pattern(self.url_parts) |should| equal_to(expected)

        @fudge.test
        it "returns '^.*' without dollar sign if string_from_url_parts is '' or '/' and self.catch_all":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns('/')
                .next_call().with_args(self.url_parts).returns('')
                )

            self.options.catch_all = True
            for expected in ('^.*', '^.*'):
                self.options.create_pattern(self.url_parts) |should| equal_to(expected)

        @fudge.test
        it "returns result of string_from_url_parts without leading slashes if ends with slash":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns('asdf/')
                .next_call().with_args(self.url_parts).returns('/jlkl/')
                .next_call().with_args(self.url_parts).returns('qwer/')
                .next_call().with_args(self.url_parts).returns("/ghjd/")
                )

            for expected in ('^asdf/', '^jlkl/', '^qwer/', '^ghjd/'):
                self.options.create_pattern(self.url_parts) |should| equal_to(expected)

        @fudge.test
        it "returns with trailing /$ if doesn't already have trailing slash":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns('asdf')
                .next_call().with_args(self.url_parts).returns('/jlkl')
                .next_call().with_args(self.url_parts).returns('qwer')
                .next_call().with_args(self.url_parts).returns("/ghjd")
                )

            for expected in ('^asdf/$', '^jlkl/$', '^qwer/$', '^ghjd/$'):
                self.options.create_pattern(self.url_parts) |should| equal_to(expected)

        @fudge.test
        it "returns with no trailing slash or dollar sign if catch_all":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns('asdf')
                .next_call().with_args(self.url_parts).returns('/jlkl')
                .next_call().with_args(self.url_parts).returns('qwer')
                .next_call().with_args(self.url_parts).returns("/ghjd")
                )

            self.options.catch_all = True
            for expected in ('^asdf', '^jlkl', '^qwer', '^ghjd'):
                self.options.create_pattern(self.url_parts) |should| equal_to(expected)

    describe "Getting string from url_parts":
        before_each:
            self.options = Options()

        it "returns None if url_parts is None":
            self.options.string_from_url_parts(None) |should| be(None)

        it "returns None if url_parts is array of [None]":
            self.options.string_from_url_parts([None]) |should| be(None)

        it "joins url_parts with / and removes multiple slashes if not None":
            tests = (
                  ("asdf/asdf", "asdf/asdf")
                , ("/asdf/asdf/", "/asdf/asdf/")
                , ("///asdf////asdf", "/asdf/asdf")
                , ("/asdf///asdf///asdf/", "/asdf/asdf/asdf/")
                , (['asdf', '/asdf', 'asdf/', '///'], 'asdf/asdf/asdf/')
                , (['/', '/', '/'], '/')
                , (['one', '', 'two', ''], 'one/two/')
                , (['one', 'two', 'three'], 'one/two/three')
                )
            for original, result in tests:
                self.options.string_from_url_parts(original) |should| equal_to(result)

    describe "Getting Url view":
        before_each:
            self.kls = fudge.Fake("kls")
            self.target = fudge.Fake("target")
            self.section = fudge.Fake("section")
            self.redirect = fudge.Fake("redirect")
            self.extra_context = fudge.Fake("extra_context")
            self.redirected_view = fudge.Fake("redirected_view")

            self.fake_get_view_kls = fudge.Fake("get_view_kls")
            self.fake_redirect_view = fudge.Fake("redirect_view")
            self.options = type("Options", (Options, )
                , {'get_view_kls' : self.fake_get_view_kls, 'redirect_view' : self.fake_redirect_view}
            )()

        @fudge.test
        it "returns redirect_view if self.redirect is set":
            self.fake_redirect_view.expects_call().with_args(self.redirect).returns(self.redirected_view)
            self.options.redirect = self.redirect
            self.options.url_view(self.section) |should| be(self.redirected_view)

        @fudge.test
        it "returns (target, self.extra_context) if target is callable":
            self.options.extra_context = self.extra_context
            for target in (self.target, lambda: 1):
                self.options.target = target
                self.options.url_view(self.section) |should| equal_to((target, self.extra_context))

        @fudge.test
        it "returns None if target isn't defined":
            self.options.target = None
            self.options.extra_context = {}
            self.options.url_view(self.section) |should| be(None)

        @fudge.patch("cwf.sections.options.dispatcher")
        it "returns (dispatcher, {self.get_view_kls(), target}) otherwise", fake_dispatcher:
            self.options.target = "thing"
            self.options.extra_context = {}
            self.fake_get_view_kls.expects_call().returns(self.kls)
            self.options.url_view(self.section) |should| equal_to(
                (fake_dispatcher, {'kls':self.kls, 'target':"thing"})
            )

        @fudge.patch("cwf.sections.options.dispatcher")
        it "returns self.extra_context with dispatcher", fake_dispatcher:
            self.options.target = "thing"
            self.options.extra_context = {'one' : 1, 'two' : 2, 'kls' : 3}
            self.fake_get_view_kls.expects_call().returns(self.kls)
            self.options.url_view(self.section) |should| equal_to(
                (fake_dispatcher, {'kls':self.kls, 'target':"thing", 'one' : 1, 'two' : 2})
            )

    describe "Getting redirect view":
        it "returns a callable and self.extra_context":
            options = Options()
            extra_context = fudge.Fake("extra_context")
            options.extra_context = extra_context

            returned = options.redirect_view(fudge.Fake("redirect"))
            callable(returned[0]) |should| be(True)
            returned[1] |should| be(extra_context)

        describe "returned callable":
            before_each:
                self.request = fudge.Fake("request").has_attr(method="GET")
                self.redirect = fudge.Fake("redirect")
                self.options = Options()

            def assertRedirectsTo(self, redirect, destination):
                redirect.status_code |should| equal_to(301)
                redirect.get('Location') |should| equal_to(destination)

            @fudge.test
            it "raises 404 if redirect is None":
                redirector, _ = self.options.redirect_view(None)
                caller = lambda : redirector(self.request)
                Http404 |should| be_thrown_by(caller)

            @fudge.test
            it "raises 404 if redirect is callable and result of calling it is None":
                self.redirect.expects_call().with_args(self.request).returns(None)
                redirector, _ = self.options.redirect_view(self.redirect)
                caller = lambda : redirector(self.request)
                Http404 |should| be_thrown_by(caller)

            @fudge.test
            it "uses self.redirect with url if it starts with /":
                url = '/somewhere/nice'
                self.redirect.expects_call().with_args(self.request).returns(url)

                redirector, _ = self.options.redirect_view(self.redirect)
                self.assertRedirectsTo(redirector(self.request), url)

                redirector2, _ = self.options.redirect_view('/stuff/asdf')
                self.assertRedirectsTo(redirector2(self.request), '/stuff/asdf')

            @fudge.test
            it "joins with request.path and removes multiple slashes if not starts with /":
                self.redirect.expects_call().with_args(self.request).returns('one/two')

                redirector, _ = self.options.redirect_view(self.redirect)
                self.request.path = '/asdf/hla/'
                self.assertRedirectsTo(redirector(self.request), '/asdf/hla/one/two')

                redirector2, _ = self.options.redirect_view('stuff/asdf')
                self.request.path = '/asdf/hla/'
                self.assertRedirectsTo(redirector2(self.request), '/asdf/hla/stuff/asdf')

        describe "Getting view kls":
            before_each:
                self.kls = fudge.Fake("kls")
                self.module = fudge.Fake("module")
                self.cleaned_kls = fudge.Fake("cleaned_kls")
                self.cleaned_module = fudge.Fake("cleaned_module")
                self.fake_clean_module_name = fudge.Fake("clean_module_name")
                self.options = type("Options", (Options, ), {'clean_module_name' : self.fake_clean_module_name})()

            it "returns None if neither self.kls or self.module":
                self.options.kls = None
                self.options.module = None
                self.options.get_view_kls() |should| be(None)

            it "returns self.kls if self.kls is truthy and not a string":
                self.options.kls = self.kls
                self.options.get_view_kls() |should| be(self.kls)

            it "cleans kls name and returns as is if no module":
                self.fake_clean_module_name.expects_call().with_args("klsname").returns(self.cleaned_kls)
                self.options.kls = "klsname"
                self.options.get_view_kls() |should| be(self.cleaned_kls)

            it "returns 'module.kls' as string if module is also string":
                (self.fake_clean_module_name.expects_call()
                    .with_args("klsname").returns(self.cleaned_kls)
                    .next_call().with_args("modulename").returns(self.cleaned_module)
                    )

                self.options.kls = "klsname"
                self.options.module = "modulename"
                self.options.get_view_kls() |should| equal_to("%s.%s" % (self.cleaned_module, self.cleaned_kls))

            it "access kls on module as attribute if module is not a string":
                (self.fake_clean_module_name.expects_call()
                    .with_args("one.two.three.four").returns("cleaned.one.two.three.four")
                    )

                four = fudge.Fake("four")
                self.options.kls = "one.two.three.four"
                self.options.module = self.module
                self.options.module.cleaned = fudge.Fake("cleaned")
                self.options.module.cleaned.one = fudge.Fake("one")
                self.options.module.cleaned.one.two = fudge.Fake("two")
                self.options.module.cleaned.one.two.three = fudge.Fake("three")
                self.options.module.cleaned.one.two.three.four = four

                self.options.get_view_kls() |should| be(four)

        describe "Cleaning name to be used as kls or module":
            before_each:
                self.options = Options()

            it "returns None if name is None":
                self.options.clean_module_name(None) |should| be(None)

            it "complains if any spaces are in the name":
                caller = lambda : self.options.clean_module_name("asdf asdf")
                caller |should| throw(ConfigurationError
                    , message="'asdf asdf' is not a valid import location (has spaces)"
                    )

            it "complains if any portion of the name seperated by dot isn't a valid variable name":
                caller = lambda : self.options.clean_module_name("asdf.1blah.things")
                caller |should| throw(ConfigurationError
                    , message="'asdf.1blah.things' is not a valid import location ('1blah' isn't a valid variable name)"
                    )

            it "removes trailing and leading dots":
                self.options.clean_module_name("...asdf.blah.things...") |should| equal_to("asdf.blah.things")
