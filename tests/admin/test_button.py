# coding: spec

from cwf.admin.buttons import Button

import fudge

describe "Button":
    before_each:
        self.a = fudge.Fake("a")
        self.b = fudge.Fake("b")
        self.url = fudge.Fake("url")
        self.desc = fudge.Fake("desc")
        self.button = Button(self.url, self.desc, a=self.a, b=self.b)

    it "sets group to False":
        self.button.group |should| be(False)

    it "sets url, desc and extra kwargs on the button":
        self.button.url |should| be(self.url)
        self.button.desc |should| be(self.desc)
        self.button.kwargs |should| equal_to({'a':self.a, 'b':self.b})

    describe "Getting html":
        before_each:
            self.html = fudge.Fake("html")
            self.fake_determine_html = fudge.Fake("determine_html")
            self.button = type("Button", (Button, )
                , { 'determine_html' : self.fake_determine_html
                  }
                )(self.url, self.desc)

        @fudge.test
        it "gets result of determine_html":
            self.fake_determine_html.expects_call().returns(self.html)
            self.button.html |should| be(self.html)

        @fudge.test
        it "caches result as self._html":
            self.fake_determine_html.expects_call().times_called(1).returns(self.html)

            self.button |should_not| respond_to("_html")
            self.button.html |should| be(self.html)

            self.button._html |should| be(self.html)

            # Call it multiple times to make times_called(1) complain if value not cached
            self.button.html |should| be(self.html)
            self.button.html |should| be(self.html)

    describe "Creating a copy for a request":
        @fudge.patch("cwf.admin.buttons.ButtonWrap")
        it "returns a ButtonWrap wrapping itself", fakeButtonWrap:
            wrap = fudge.Fake("wrap")
            request = fudge.Fake("request")
            original = fudge.Fake("original")
            fakeButtonWrap.expects_call().with_args(self.button, request, original).returns(wrap)
            self.button.copy_for_request(request, original=original) |should| be(wrap)

    describe "Determining html":
        before_each:
            self.fake_link_as_input = fudge.Fake("link_as_input")
            self.fake_link_as_anchor = fudge.Fake("link_as_anchor")

        def make_button(self, save_on_click=True, for_all=False):
            return type("button", (Button, )
                , { 'for_all' : for_all
                  , 'save_on_click' : save_on_click
                  , 'link_as_input' : self.fake_link_as_input
                  , 'link_as_anchor' : self.fake_link_as_anchor
                  }
                )(self.url, self.desc)

        @fudge.patch("cwf.admin.buttons.mark_safe")
        it "returns safe marked link as an anchor if not save_on_click or for_all", fake_mark_safe:
            spec = [
                  (False, True)
                , (False, False)
                , (True, True)
                ]

            html = fudge.Fake("html")
            safe_html = fudge.Fake("safe_html")
            fake_mark_safe.expects_call().with_args(html).returns(safe_html)

            # Anchor is the one that is called
            self.fake_link_as_anchor.expects_call().times_called(3).returns(html)

            for save_on_click, for_all in spec:
                button = self.make_button(save_on_click=save_on_click, for_all=for_all)
                button.determine_html() |should| be(safe_html)

        @fudge.patch("cwf.admin.buttons.mark_safe")
        it "returns safe marked link as input if not for all and saves on click", fake_mark_safe:
            html = fudge.Fake("html")
            safe_html = fudge.Fake("safe_html")
            fake_mark_safe.expects_call().with_args(html).returns(safe_html)

            # Anchor is the one that is called
            self.fake_link_as_input.expects_call().returns(html)

            button = self.make_button(save_on_click=True, for_all=False)
            button.determine_html() |should| be(safe_html)

    describe "Getting link as an input":
        it "returns submit input with name as tool_<self.url> and value as self.desc":
            expected = '<input type="submit" name="tool_%s" value="%s"/>' % (self.url, self.desc)
            self.button.link_as_input() |should| equal_to(expected)

    describe "Getting link as an anchor":
        it "returns anchor with href as url and value as desc":
            expected = '<a href="%s" >%s</a>' % (self.url, self.desc)
            self.button.save_on_click = False
            self.url.expects("startswith").with_args('/').returns(True)
            self.button.link_as_anchor() |should| equal_to(expected)

        it "adds kls as a html class":
            expected = '<a href="%s" class="blah and things">%s</a>' % (self.url, self.desc)
            self.button.save_on_click = False
            self.button.kls = "blah and things"
            self.url.expects("startswith").with_args('/').returns(True)
            self.button.link_as_anchor() |should| equal_to(expected)

        it 'adds target="_blank" if new_window is true':
            expected = '<a href="%s" target="_blank">%s</a>' % (self.url, self.desc)
            self.button.new_window = True
            self.button.save_on_click = False
            self.url.expects("startswith").with_args('/').returns(True)
            self.button.link_as_anchor() |should| equal_to(expected)

        it "prepends url with tool_ if save_on_click":
            expected = '<a href="tool_%s" >%s</a>' % (self.url, self.desc)
            self.button.save_on_click = True
            self.button.link_as_anchor() |should| equal_to(expected)

        it "prepends url with tool_ if url doesn't start with slash":
            expected = '<a href="tool_%s" >%s</a>' % (self.url, self.desc)
            self.button.save_on_click = False
            self.url.expects("startswith").with_args('/').returns(False)
            self.button.link_as_anchor() |should| equal_to(expected)

        it "works with combination of the above":
            expected = '<a href="tool_%s" class="things and stuff" target="_blank">%s</a>' % (self.url, self.desc)
            self.button.kls = "things and stuff"
            self.button.new_window = True
            self.button.save_on_click = True
            self.button.link_as_anchor() |should| equal_to(expected)
