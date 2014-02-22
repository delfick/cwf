# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should, should_not
from django.test import TestCase

from cwf.admin.buttons import ButtonBase, ButtonProperties

import fudge

# Make the errors go away
be, respond_to, equal_to, contain = None, None, None, None

describe TestCase, "Button properties":
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
            , ('return_to_form', False)
            , ('need_super_user', True)
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

describe TestCase, "Button Base":
    before_each:
        self.button = ButtonBase()

    describe "Attribute Access":
        before_each:
            self.url = fudge.Fake("url")
            self.properties = fudge.Fake("properties")
            self.button = type("button", (ButtonBase, )
                , { "properties" : self.properties
                  }
                )()
            object.__setattr__(self.button, 'url', self.url)

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

            button = type("button", (ButtonBase, ), {'one' : one})()
            button.properties.one = one2

            button.one |should| be(one)
            button.properties.one |should| be(one2)

            button.one = one3
            button.one |should| be(one3)
            button.properties.one |should| be(one2)

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
