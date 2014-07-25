# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should
from django.test import TestCase

from django.template.loader import get_template_from_string
from django.template import Template
from django.http import Http404

from cwf.views.rendering import Renderer, renderer

import fudge

# Make the errors go away
be, equal_to = None, None

describe TestCase, "Rendering helper":
    before_each:
        self.helper = renderer

    describe "Simple render":
        it "returns specified template with provided variables":
            rendered = self.helper.simple_render("rendering/complex.html", {'blah':'things'})
            rendered |should| equal_to("<p><a>things</a></p>")

            rendered = self.helper.simple_render("rendering/complex.html", {'blah':'other'})
            rendered |should| equal_to("<p><a>other</a></p>")

    describe "Complex render":
        before_each:
            self.mime = fudge.Fake("mime")
            self.extra = fudge.Fake("extra")
            self.template = fudge.Fake("template")
            self.request = fudge.Fake("request")
            self.fake_request_context = fudge.Fake("request_context")
            self.helper = type("renderer", (Renderer, )
                , { 'request_context' : self.fake_request_context
                  }
                )()

        @fudge.patch("cwf.views.rendering.HttpResponse", "cwf.views.rendering.loader")
        it "renders template with request context", fakeHttpResponse, fake_loader:
            ctxt = fudge.Fake("ctxt")
            self.fake_request_context.expects_call().with_args(self.request, self.extra).returns(ctxt)

            # Loader gives us a template object
            # Which is used to get us the render
            render = fudge.Fake("render")
            template_obj = fudge.Fake("template_obj").expects("render").with_args(ctxt).returns(render)
            fake_loader.expects("get_template").with_args(self.template).returns(template_obj)

            # Our result is a HttpResponse object
            result = fudge.Fake("result")
            fakeHttpResponse.expects_call().with_args(render, content_type=self.mime).returns(result)

            self.helper.render(self.request, self.template, extra=self.extra, mime=self.mime) |should| be(result)

        @fudge.patch("cwf.views.rendering.HttpResponse", "cwf.views.rendering.loader")
        it "uses template as is if it's a Template object", fakeHttpResponse, fake_loader:
            ctxt = fudge.Fake("ctxt")
            self.fake_request_context.expects_call().with_args(self.request, self.extra).returns(ctxt)

            render_result = fudge.Fake("render_result")
            render = fudge.Fake("render").expects_call().with_args(ctxt).returns(render_result)
            template = get_template_from_string("<html></html>")

            # Our result is a HttpResponse object
            result = fudge.Fake("result")
            fakeHttpResponse.expects_call().with_args(render_result, content_type=self.mime).returns(result)

            with fudge.patched_context(template, 'render', render):
                self.helper.render(self.request, template, extra=self.extra, mime=self.mime) |should| be(result)

        @fudge.patch("cwf.views.rendering.HttpResponse", "cwf.views.rendering.loader")
        it "modifies render before giving to HttpResponse if modify is callable", fakeHttpResponse, fake_loader:
            ctxt = fudge.Fake("ctxt")
            self.fake_request_context.expects_call().with_args(self.request, self.extra).returns(ctxt)

            # Loader gives us a template object
            # Which is used to get us the render
            render = fudge.Fake("render")
            template_obj = fudge.Fake("template_obj").expects("render").with_args(ctxt).returns(render)
            fake_loader.expects("get_template").with_args(self.template).returns(template_obj)

            # Render is modified
            result = fudge.Fake("result")
            modified = fudge.Fake("modified")
            modify = (fudge.Fake("modify").expects_call()
                .with_args(render).returns(modified)
                )

            # Our result is a HttpResponse object
            fakeHttpResponse.expects_call().with_args(modified, content_type=self.mime).returns(result)

            self.helper.render(self.request, self.template
                , extra=self.extra, mime=self.mime, modify=modify
                ) |should| be(result)

    describe "Getting request context":
        before_each:
            self.extra = fudge.Fake("extra")
            self.state = fudge.Fake("state")
            self.request = fudge.Fake("request")

        @fudge.patch("cwf.views.rendering.RequestContext")
        it "gets context from request.state", fakeRequestContext:
            self.request.state = self.state
            self.state.expects("update").with_args(self.extra)

            result = fudge.Fake("result")
            fakeRequestContext.expects_call().with_args(self.request, self.state).returns(result)

            self.helper.request_context(self.request, self.extra) |should| be(result)

        @fudge.patch("cwf.views.rendering.RequestContext")
        it "uses empty dictionary if request has no state", fakeRequestContext:
            a = fudge.Fake("a")
            b = fudge.Fake("b")

            result = fudge.Fake("result")
            fakeRequestContext.expects_call().with_args(self.request, {'a':a, 'b':b}).returns(result)

            self.helper.request_context(self.request, {'a':a, 'b':b}) |should| be(result)

    describe "Raising 404":
        it "raises Http404":
            with self.assertRaises(Http404):
                self.helper.raise404()

    describe "Shortcut to a HttpResponse":
        @fudge.patch("cwf.views.rendering.HttpResponse")
        it "Passes in args and kwargs into a httpresponse", fakeHttpResponse:
            a = fudge.Fake('a')
            b = fudge.Fake('b')
            c = fudge.Fake('c')
            d = fudge.Fake('d')
            result = fudge.Fake('result')
            fakeHttpResponse.expects_call().with_args(a, b, c=c, d=d).returns(result)
            self.helper.http(a, b, c=c, d=d) |should| be(result)

    describe "Shortcut to render xml":
        @fudge.patch("cwf.views.rendering.HttpResponse")
        it "returns HttpResponse with application/xml content_type", fakeHttpResponse:
            data = fudge.Fake("data")
            result = fudge.Fake("result")
            fakeHttpResponse.expects_call().with_args(data, content_type="application/xml").returns(result)
            self.helper.xml(data) |should| be(result)

    describe "shortcut to render json":
        @fudge.patch("cwf.views.rendering.HttpResponse", "json.dumps")
        it "returns HttpResponse with application/javascript content_type after converting data to json string", fakeHttpResponse, fake_dumps:
            data = fudge.Fake("data")
            json = fudge.Fake("json")
            fake_dumps.expects_call().with_args(data).returns(json)

            result = fudge.Fake("result")
            fakeHttpResponse.expects_call().with_args(json, content_type="application/javascript").returns(result)
            self.helper.json(data) |should| be(result)

        @fudge.patch("cwf.views.rendering.HttpResponse", "json.dumps")
        it "assumes data is already json if passed in as a string", fakeHttpResponse, fake_dumps:
            json = '{"a":"b"}'
            result = fudge.Fake("result")
            fakeHttpResponse.expects_call().with_args(json, content_type="application/javascript").returns(result)
            self.helper.json(json) |should| be(result)

    describe "Getting a redirect":
        before_each:
            self.address = fudge.Fake("address")
            self.request = fudge.Fake("request")

        @fudge.patch("cwf.views.rendering.HttpResponseRedirect")
        it "Returns if HttpResponseRedirect with no change to address if no_processing=True", fakeHttpResponseRedirect:
            result = fudge.Fake("result")
            fakeHttpResponseRedirect.expects_call().with_args(self.address).returns(result)
            self.helper.redirect(self.request, self.address, no_processing=True) |should| be(result)

        @fudge.patch("cwf.views.rendering.HttpResponseRedirect", "cwf.views.rendering.RedirectAddress")
        it "modifies address before passing into HttpResponseRedirect if no_processing=False or not specified", fakeHttpResponseRedirect, fakeRedirectAddress:
            a = fudge.Fake('a')
            b = fudge.Fake('b')
            c = fudge.Fake('c')
            d = fudge.Fake('d')
            result1 = fudge.Fake("result1")
            result2 = fudge.Fake("result2")
            modified1 = fudge.Fake("modified1")
            modified2 = fudge.Fake("modified2")
            redirect1 = fudge.Fake("redirect1").has_attr(modified=modified1)
            redirect2 = fudge.Fake("redirect2").has_attr(modified=modified2)

            (fakeRedirectAddress.expects_call()
                .with_args(self.request, self.address, a, b, c=c, d=d).returns(redirect1)
                .next_call().with_args(self.request, self.address, a, b, c=c, d=d).returns(redirect2)
                )

            (fakeHttpResponseRedirect.expects_call()
                .with_args(modified1).returns(result1)
                .next_call().with_args(modified2).returns(result2)
                )

            self.helper.redirect(self.request, self.address, a, b, c=c, d=d) |should| be(result1)
            self.helper.redirect(self.request, self.address, a, b, c=c, d=d, no_processing=False) |should| be(result2)
