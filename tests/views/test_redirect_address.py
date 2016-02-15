# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should
from django.test import TestCase

from cwf.views.redirect_address import RedirectAddress

import fudge

# Make the errors go away
be, equal_to = None, None

describe TestCase, "RedirectAddress":
    before_each:
        self.request = fudge.Fake("request")
        self.addr = fudge.Fake("address")
        self.helper = RedirectAddress(self.request, self.addr)

    describe "defaults":
        it "defaults to relative being true":
            self.helper.relative |should| be(True)

        it "defaults carry_get to False":
            self.helper.carry_get |should| be(False)

        it "defaults ignore_get to None":
            self.helper.ignore_get |should| be(None)

    describe "Getting modified address":
        before_each:
            self.fake_modify = fudge.Fake("modify")
            self.helper = type("redirectaddress", (RedirectAddress, )
                , { 'modify' : self.fake_modify
                  }
                )(self.request, self.addr)

        @fudge.test
        it "modifies the unicode of self.addr":
            modified = fudge.Fake("modified")
            self.helper.address = type("Address", (object, )
                , {"__unicode__":lambda s : "unicode version of address"
                  }
                )()
            self.fake_modify.expects_call().with_args("unicode version of address").returns(modified)
            self.helper.modified |should| be(modified)

    describe "Modifying an address":
        before_each:
            self.fake_joined_address = fudge.Fake("joined_address")
            self.fake_add_get_params = fudge.Fake("add_get_params")
            self.fake_strip_multi_slashes = fudge.Fake("strip_multi_slashes")
            self.helper = type("redirectaddress", (RedirectAddress, )
                , { 'joined_address' : self.fake_joined_address
                  , 'add_get_params' : self.fake_add_get_params
                  , 'strip_multi_slashes' : self.fake_strip_multi_slashes
                  }
                )(self.request, self.addr)

        @fudge.test
        it "joines the address, removes slashes and adds GET params":
            mod1 = fudge.Fake("mod1")
            mod2 = fudge.Fake("mod2")
            mod3 = fudge.Fake("mod3")
            address = fudge.Fake("address")

            self.fake_joined_address.expects_call().with_args(address).returns(mod1)
            self.fake_strip_multi_slashes.expects_call().with_args(mod1).returns(mod2)
            self.fake_add_get_params.expects_call().with_args(mod2).returns(mod3)

            self.helper.modify(address) |should| be(mod3)

    describe "Getting base url":
        before_each:
            self.request = fudge.Fake("request")
            self.helper.request = self.request

        it "gets baseUrl from request.state if request has that":
            base_url = fudge.Fake("base_url")
            state = fudge.Fake("state").has_attr(base_url=base_url)
            self.request.has_attr(state=state)
            self.helper.base_url |should| be(base_url)

        it "gets base url from META['SCRIPT_NAME'] if request has no state":
            base_url = fudge.Fake("base_url")
            meta = {'SCRIPT_NAME' : base_url}
            self.request.has_attr(META=meta)
            self.helper.base_url |should| be(base_url)

        it "gets empty string if no request.state and no META['SCRIPT_NAME']":
            meta = {}
            self.request.has_attr(META=meta)
            self.helper.base_url |should| be("")

    describe "Getting params":
        it "returns request.GET if nothing needs to be ignored from it":
            get = fudge.Fake("get")
            self.request.GET = get

            # By default nothing gets ignored
            self.helper.params |should| be(get)

            # Nothing is ignored if ignore_get is False
            self.request.ignore_get = False
            self.helper.params |should| be(get)

        it "filters params by ignoring whats in ignore_get":
            ignore_get = ['a', 'b', 'c']
            get = {'a':1, 'b':2, 'd':3, 'e':4}
            self.request.GET = get
            self.helper.ignore_get = ignore_get

            self.helper.params |should| equal_to({'d':3, 'e':4})

    describe "Replacing multiple slashes with single slashes":
        it "does exactly that":
            specs = [
                  ("", "")
                , ("/", "/")
                , ("//", "/")
                , ("////", "/")
                , ("/a/", "/a/")
                , ("//a", "/a")
                , ("////aasdf///sadf/a/sdf/d///", "/aasdf/sadf/a/sdf/d/")
                ]

            for original, result in specs:
                self.helper.strip_multi_slashes(original) |should| equal_to(result)

    describe "Determining if a url is a root address":
        it "says True if address begins with a slash":
            self.helper.root_url("/asdf/asdf") |should| be(True)

        it "says False if address doesn't begin with a slash":
            self.helper.root_url("asdf/asdf") |should| be(False)

    describe "Adding get params to an address":
        before_each:
            self.params = fudge.Fake("params")
            self.addr = fudge.Fake("address")
            self.helper = type("redirectaddress", (RedirectAddress, )
                , { 'params' : self.params
                  }
                )(self.request, self.addr)

        @fudge.patch("cwf.views.redirect_address.urlencode")
        it "returns address as is if carry_get is False", fake_urlencode:
            self.helper.carry_get = False
            self.helper.add_get_params(self.addr) |should| be(self.addr)

        @fudge.patch("cwf.views.redirect_address.urlencode")
        it "returns combination of address and urlencoded params if carry_get is True", fake_urlencode:
            encoded = fudge.Fake("encoded")
            fake_urlencode.expects_call().with_args(self.params).returns(encoded)

            self.helper.carry_get = True
            self.helper.add_get_params(self.addr) |should| equal_to("%s?%s" % (self.addr, encoded))

    describe "Getting full url from address":
        before_each:
            self.base_url = fudge.Fake("base_url")
            self.fake_url_join = fudge.Fake("url_join")
            self.fake_root_url = fudge.Fake("root_url")

            self.helper = type("redirectAddress", (RedirectAddress, )
                , { 'base_url' : self.base_url
                  , 'url_join' : self.fake_url_join
                  , 'root_url' : self.fake_root_url
                  }
                )(self.request, self.addr)

        @fudge.test
        it "joins with base_url if a root url":
            joined = fudge.Fake("joined")
            address = fudge.Fake("address")

            self.fake_root_url.expects_call().with_args(address).returns(True)
            self.fake_url_join.expects_call().with_args(self.base_url, address).returns(joined)

            self.helper.joined_address(address) |should| be(joined)

        @fudge.test
        it "joins with request.path if not a root url and relative is True":
            path = fudge.Fake("path")
            joined = fudge.Fake("joined")
            address = fudge.Fake("address")

            self.request.has_attr(path=path)
            self.fake_root_url.expects_call().with_args(address).returns(False)
            self.fake_url_join.expects_call().with_args(path, address).returns(joined)

            self.helper.relative = True
            self.helper.joined_address(address) |should| be(joined)

        @fudge.test
        it "returns as is if not a root url and relative is False":
            address = fudge.Fake("address")

            self.fake_root_url.expects_call().with_args(address).returns(False)

            self.helper.relative = False
            self.helper.joined_address(address) |should| be(address)

    describe "Joining two urls":
        it "joins both as is if either is empty":
            self.helper.url_join("", "asdf") |should| equal_to("asdf")
            self.helper.url_join("asdf", "") |should| equal_to("asdf")

        it "joins with nothing in between if there is already slash in between":
            specs = [
                  ('/', 'asdf', '/asdf')
                , ('/', '/asdf', '//asdf')
                , ('asdf', '/', 'asdf/')
                , ('asdf/', '/', 'asdf//')
                , ('asdf/', '/asdf', 'asdf//asdf')
                , ('/asdf/', '/asdf/', '/asdf//asdf/')
                ]

            for a, b, expected in specs:
                self.helper.url_join(a, b) |should| equal_to(expected)

        it "joins with a slash in between if one not already there":
            specs = [
                  ('/bob', 'asdf', '/bob/asdf')
                , ('asdf', 'bob/asdf', 'asdf/bob/asdf')
                , ('asdf', 'asdf', 'asdf/asdf')
                , ('/asdf', 'asdf/', '/asdf/asdf/')
                ]

            for a, b, expected in specs:
                self.helper.url_join(a, b) |should| equal_to(expected)
