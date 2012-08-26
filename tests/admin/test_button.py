# coding: spec

from cwf.admin.buttons import Button, ButtonProperties

import fudge

describe "Button properties":
    it "makes sure save_on_click is False if for_all is True":
        properties = ButtonProperties({'for_all':True})
        properties._kwargs |should| equal_to({'for_all':True, 'save_on_click':False})

        properties = ButtonProperties({'for_all':True, 'save_on_click':True})
        properties._kwargs |should| equal_to({'for_all':True, 'save_on_click':False})

        # Make sure it's left alone if for_all is False
        properties = ButtonProperties({'for_all':False, 'save_on_click':False})
        properties._kwargs |should| equal_to({'for_all':False, 'save_on_click':False})

        # Make sure nothing happens if for_all is not there
        properties = ButtonProperties({})
        properties._kwargs |should| equal_to({})

    it "has defaults":
        properties = ButtonProperties({})
        properties._defaults |should| equal_to(dict(
            [ ('kls', None)
            , ('display', True)
            , ('for_all', False)
            , ('condition', None)
            , ('new_window', False)
            , ('needs_auth', None)
            , ('description', None)
            , ('save_on_click', True)
            , ('need_super_user', True)
            , ('execute_and_redirect', False)
            ]
            )
        )

    it "attribute accesses from defaults if key not in kwargs":
        properties = ButtonProperties({})
        assert 'save_on_click' not in properties._kwargs

        save_on_click = fudge.Fake('save_on_click')
        properties._defaults['save_on_click'] = save_on_click
        properties.save_on_click |should| be(save_on_click)

    it "attribute accesses from kwargs if key in kwargs":
        properties = ButtonProperties({})
        properties.need_super_user |should| be(True)

        need_super_user = fudge.Fake("need_super_user")
        properties._kwargs = dict(need_super_user=need_super_user)
        properties.need_super_user |should| be(need_super_user)

    it "raises AttributeError if key in neither _kwargs or _defaults":
        with self.assertRaises(AttributeError):
            assert ButtonProperties({}).asdfkljlskadfj

    it "puts values into kwargs on attribute setting":
        properties = ButtonProperties({})
        properties._kwargs |should| equal_to({})

        one = fudge.Fake("one")
        two = fudge.Fake("two")
        properties.one = one
        properties.two = two

        properties._kwargs |should| equal_to(dict(one=one, two=two))

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

    describe "Attribute Access":
        before_each:
            self.properties = fudge.Fake("properties")
            self.button = type("button", (Button, )
                , { "properties" : self.properties
                  }
                )(self.url, self.desc)

        it "gets attribute from properties unless attribute is on button":
            url = fudge.Fake("url")
            blah = fudge.Fake("blah")
            blah2 = fudge.Fake("blah2")
            self.properties.has_attr(blah=blah, url=url)

            self.button.url |should| be(self.url)
            self.button.properties.url |should| be(url)

            # Blah not on button, comes from properties
            self.button.blah |should| be(blah)

            # Put blah onto button as blah2
            # So button gets blah from itself
            object.__setattr__(self.button, 'blah', blah2)
            self.button.blah |should| be(blah2)

    describe "Attribute Setting":
        it "sets attributes onto properties if key already in properties":
            self.button.properties |should| respond_to("save_on_click")

            self.button.save_on_click |should| be(True)
            self.button.__dict__ |should_not| contain('save_on_click')
            self.button.properties.save_on_click |should| be(True)

            self.button.save_on_click = False
            self.button.save_on_click |should| be(False)
            self.button.__dict__ |should_not| contain('save_on_click')
            self.button.properties.save_on_click |should| be(False)

        it "sets attributes onto button if key already on button":
            one = fudge.Fake("one")
            one2 = fudge.Fake("one2")
            one3 = fudge.Fake("one3")

            button = type("button", (Button, ), {'one' : one})(self.url, self.desc)
            button.properties.one = one2

            button.one |should| be(one)
            button.properties.one |should| be(one2)

            button.one = one3
            button.one |should| be(one3)
            button.properties.one |should| be(one2)

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

    describe "Getting properties":
        before_each:
            self.kwargs = fudge.Fake("kwargs")
            self.properties = fudge.Fake("properties")

        @fudge.patch("cwf.admin.buttons.ButtonProperties")
        it "creates a ButtonProperties object with self.kwargs", fakeButtonProperties:
            object.__setattr__(self.button, 'kwargs', self.kwargs)
            fakeButtonProperties.expects_call().times_called(1).with_args(self.kwargs).returns(self.properties)
            self.button.properties |should| be(self.properties)

        @fudge.patch("cwf.admin.buttons.ButtonProperties")
        it "caches result as self._properties", fakeButtonProperties:
            object.__setattr__(self.button, 'kwargs', self.kwargs)
            fakeButtonProperties.expects_call().times_called(1).with_args(self.kwargs).returns(self.properties)

            self.button |should_not| respond_to("_properties")
            self.button.properties |should| be(self.properties)

            self.button._properties |should| be(self.properties)

            # Call it multiple times to make times_called(1) complain if value not cached
            self.button._properties |should| be(self.properties)
            self.button._properties |should| be(self.properties)

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
