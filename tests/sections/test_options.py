# coding: spec

from src.sections.errors import ConfigurationError
from src.sections.options import Options

from django.http import Http404
import fudge

describe "Options":
    describe "Creating patterns":
        before_each:
            self.url_parts = fudge.Fake("url_parts")
            self.fake_string_from_url_parts = fudge.Fake("string_from_url_parts")
            self.options = type("Options", (Options, ), {'string_from_url_parts' : self.fake_string_from_url_parts})()
        
        @fudge.test
        it "returns '.*' if string_from_url_parts is None":
            self.fake_string_from_url_parts.expects_call().with_args(self.url_parts).returns(None)
            self.options.create_pattern(self.url_parts, start=False, end=False) |should| equal_to(".*")
        
        @fudge.test
        it "returns result of string_from_url_parts without leading or trailing slashes if not None":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns('')
                .next_call().with_args(self.url_parts).returns('/')
                .next_call().with_args(self.url_parts).returns('asdf')
                .next_call().with_args(self.url_parts).returns('/jlkl')
                .next_call().with_args(self.url_parts).returns('qwer/')
                .next_call().with_args(self.url_parts).returns("/ghjd/")
                )
            
            for expected in ('', '', 'asdf', 'jlkl', 'qwer', 'ghjd'):
                self.options.create_pattern(self.url_parts, start=False, end=False) |should| equal_to(expected)
        
        @fudge.test
        it "prepends with ^ if start is True":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns(None)
                .next_call().with_args(self.url_parts).returns('')
                .next_call().with_args(self.url_parts).returns('/')
                .next_call().with_args(self.url_parts).returns('asdf')
                .next_call().with_args(self.url_parts).returns('/jlkl')
                .next_call().with_args(self.url_parts).returns('qwer/')
                .next_call().with_args(self.url_parts).returns("/ghjd/")
                )
            
            for expected in ('^.*', '^', '^', '^asdf', '^jlkl', '^qwer', '^ghjd'):
                self.options.create_pattern(self.url_parts, start=True, end=False) |should| equal_to(expected)
        
        @fudge.test
        it "appends with $ if end is True":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns(None)
                .next_call().with_args(self.url_parts).returns('')
                .next_call().with_args(self.url_parts).returns('/')
                .next_call().with_args(self.url_parts).returns('asdf')
                .next_call().with_args(self.url_parts).returns('/jlkl')
                .next_call().with_args(self.url_parts).returns('qwer/')
                .next_call().with_args(self.url_parts).returns("/ghjd/")
                )
            
            for expected in ('.*$', '$', '$', 'asdf$', 'jlkl$', 'qwer$', 'ghjd$'):
                self.options.create_pattern(self.url_parts, start=False, end=True) |should| equal_to(expected)
        
        @fudge.test
        it "prepends with ^ and appends with $ if both start and end are True":
            (self.fake_string_from_url_parts.expects_call()
                            .with_args(self.url_parts).returns(None)
                .next_call().with_args(self.url_parts).returns('')
                .next_call().with_args(self.url_parts).returns('/')
                .next_call().with_args(self.url_parts).returns('asdf')
                .next_call().with_args(self.url_parts).returns('/jlkl')
                .next_call().with_args(self.url_parts).returns('qwer/')
                .next_call().with_args(self.url_parts).returns("/ghjd/")
                )
            
            for expected in ('^.*$', '^$', '^$', '^asdf$', '^jlkl$', '^qwer$', '^ghjd$'):
                self.options.create_pattern(self.url_parts, start=True, end=True) |should| equal_to(expected)
    
    describe "Getting string from url_parts":
        before_each:
            self.options = Options()
        
        it "returns None if url_parts is None":
            self.options.string_from_url_parts(None) |should| be(None)
        
        it "returns None if url_parts is [None]":
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
        
        @fudge.patch("src.sections.options.dispatcher")
        it "returns (dispatcher, {self.get_view_kls(), target, section}) otherwise", fake_dispatcher:
            self.options.target = "thing"
            self.options.extra_context = {}
            self.fake_get_view_kls.expects_call().returns(self.kls)
            self.options.url_view(self.section) |should| equal_to(
                (fake_dispatcher, {'kls':self.kls, 'target':"thing", 'section':self.section})
            )
        
        @fudge.patch("src.sections.options.dispatcher")
        it "returns self.extra_context with dispatcher", fake_dispatcher:
            self.options.target = "thing"
            self.options.extra_context = {'one' : 1, 'two' : 2, 'kls' : 3}
            self.fake_get_view_kls.expects_call().returns(self.kls)
            self.options.url_view(self.section) |should| equal_to(
                (fake_dispatcher, {'kls':self.kls, 'target':"thing", 'section':self.section, 'one' : 1, 'two' : 2})
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
                self.request = fudge.Fake("request")
                self.redirect = fudge.Fake("redirect")
                self.fake_redirect_to = fudge.Fake("redirect_to")
                self.options = type("Options", (Options, ), {"redirect_to" : self.fake_redirect_to})()
            
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
            it "uses self.redirect_to with url if it starts with /":
                url = fudge.Fake("url").expects("startswith").with_args("/").returns(True)
                result = fudge.Fake("result")
                self.redirect.expects_call().with_args(self.request).returns(url)
                
                (self.fake_redirect_to.expects_call()
                    .with_args(self.request, url).returns(result)
                    .next_call().with_args(self.request, '/stuff/asdf').returns(result)
                    )
                
                redirector, _ = self.options.redirect_view(self.redirect)
                redirector(self.request) |should| be(result)
                
                redirector2, _ = self.options.redirect_view('/stuff/asdf')
                redirector2(self.request) |should| be(result)
            
            @fudge.test
            it "joins with request.path and removes multiple slashes if not starts with /":
                result = fudge.Fake("result")
                self.redirect.expects_call().with_args(self.request).returns('one/two')
                
                (self.fake_redirect_to.expects_call()
                    .with_args(self.request, '/asdf/hla/one/two').returns(result)
                    .next_call().with_args(self.request, '/asdf/hla/stuff/asdf').returns(result)
                    )
                
                redirector, _ = self.options.redirect_view(self.redirect)
                self.request.path = '/asdf/hla/'
                redirector(self.request) |should| be(result)
                
                redirector2, _ = self.options.redirect_view('stuff/asdf')
                self.request.path = '/asdf/hla/'
                redirector2(self.request) |should| be(result)
        
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
