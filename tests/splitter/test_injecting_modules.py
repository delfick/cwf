# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should
from django.test import TestCase

from cwf.splitter.imports import FileFaker, steal, inject
import stolen_vars

import fudge
import imp
import os

# Make the errors go away
be, equal_to, be_greater_than = None, None, None

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'cwf'))

describe TestCase, "Injecting modules":
    def check_cant_import(self, name):
        try:
            __import__(name)
            assert False
        except ImportError:
            assert True

    def check_imported_module(self, module):
        """Assume module is stolen_vars"""
        module._hidden |should| equal_to("_hidden")
        module.a |should| equal_to("a")
        module.b |should| equal_to("b")
        module.c |should| equal_to("c")
        module.one |should| equal_to(1)
        module.two |should| equal_to(2)
        module.three |should| equal_to(3)
        hasattr(module, '__ignore') |should| be(False)

    describe "With no dot in fullname":
        it "works with modules":
            self.check_cant_import('batman')
            inject(stolen_vars, 'batman')
            mod = __import__('batman')

            mod.__file__ |should| equal_to("batman.py")
            mod.__name__ |should| equal_to("batman")
            self.check_imported_module(mod)

        it "works with dictionary":
            self.check_cant_import('hulk')
            inject({'blah':'things'}, 'hulk')
            mod = __import__('hulk')

            mod.__file__ |should| equal_to("hulk.py")
            mod.__name__ |should| equal_to("hulk")
            mod.blah |should| equal_to("things")

        it "works with non dictionary":
            val = type("val", (object, ), {})()
            self.check_cant_import('hurmph')
            inject(val, 'hurmph')
            mod = __import__('hurmph')

            mod.__file__ |should| equal_to("hurmph.py")
            mod.__name__ |should| equal_to("hurmph")
            mod.value |should| be(val)

    describe "With dot in fullname":
        it "works with modules imported with dot in fullname":
            self.check_cant_import('cwf.models')
            inject(stolen_vars, 'cwf.models')
            mod = getattr(__import__('cwf.models'), 'models')

            mod.__file__ |should| equal_to(os.path.join(src_dir, "models.py"))
            mod.__name__ |should| equal_to("cwf.models")
            self.check_imported_module(mod)

        it "works with dictionary":
            self.check_cant_import('cwf.hulk')
            inject({'blah':'things'}, 'cwf.hulk')
            mod = getattr(__import__('cwf.hulk'), 'hulk')

            mod.__file__ |should| equal_to(os.path.join(src_dir, "hulk.py"))
            mod.__name__ |should| equal_to("cwf.hulk")
            mod.blah |should| equal_to("things")

        it "works with non dictionary":
            val = type("val", (object, ), {})()
            self.check_cant_import('cwf.hurmph')
            inject(val, 'cwf.hurmph')
            mod = getattr(__import__('cwf.hurmph'), 'hurmph')

            mod.__file__ |should| equal_to(os.path.join(src_dir, "hurmph.py"))
            mod.__name__ |should| equal_to("cwf.hurmph")
            mod.value |should| be(val)

describe TestCase, "FileFaker":
    before_each:
        self.names = fudge.Fake("names")
        self.value = fudge.Fake("value")
        self.file_faker = FileFaker(self.names, self.value)

    it "takes in names and value":
        file_faker = FileFaker(self.names, self.value)
        file_faker.names |should| be(self.names)
        file_faker._value |should| be(self.value)

    describe "Getting value":
        before_each:
            self.fake_normalize_value = fudge.Fake("normalize_value")
            self.file_faker = type("Faker", (FileFaker, )
                , { 'normalize_value' : self.fake_normalize_value
                  }
                )(self.names, self.value)

        @fudge.test
        it "passes result of calling value into normalize_value if callable":
            result = fudge.Fake("result")
            normalized = fudge.Fake("normalized")

            self.value.expects_call().returns(result)
            self.fake_normalize_value.expects_call().with_args(result).returns(normalized)

            self.file_faker.value |should| be(normalized)

        @fudge.test
        it "just passes straight into normalize_value if not callable":
            value = type("value", (object, ), {})()
            normalized = fudge.Fake("normalized")

            self.file_faker._value = value
            self.fake_normalize_value.expects_call().with_args(value).returns(normalized)

            self.file_faker.value |should| be(normalized)

    describe "find_module":
        it "returns self if requested fullname is in self.names":
            self.file_faker.names = ['a', 'b.c', 'd.e.f']
            for fullname in ['a', 'b.c', 'd.e.f']:
                self.file_faker.find_module(fullname) |should| be(self.file_faker)

        it "returns None if requested fullname is not in self.names":
            self.file_faker.names = ['a', 'b.c', 'd.e.f']
            for fullname in ['t', 'r.k', 'd.e']:
                self.file_faker.find_module(fullname) |should| be(None)

    describe "Getting path from a fullname":
        it "returns ('', fullname) if fullname has no dot in it":
            for name in ('a', 'asdf', 'oiuo'):
                self.file_faker.path_from_fullname(name) |should| equal_to(('', name))

        it "gets path from looking in sys.modules with everything to the left of the last dot":
            path = fudge.Fake("path")
            modules = {'path.to.things' : type("module", (object, ), {'__path__' : [path]})()}
            with fudge.patched_context("sys", "modules", modules):
                self.file_faker.path_from_fullname("path.to.things.stuff") |should| equal_to((path, 'stuff'))

    describe "Normalizing the value":
        it "returns value as is if not a module":
            for val in (
                  0, 1, True, False, [], [1], {}, {1:2}
                , fudge.Fake("val"), type("object", (object, ), {}), type("object", (object, ), {})()
                , lambda : 2
                ):
                self.file_faker.normalize_value(val) |should| be(val)

        it "creates a dictionary of everything in __all__ if it's a module with __all__":
            args = dict(a=1, b=2, c=3, d=4, e=5, __all__=['a', 'b', 'c'])
            module = imp.new_module('name')
            module.__dict__.update(args)
            self.file_faker.normalize_value(module) |should| equal_to({'a':1, 'b':2, 'c':3})

        it "creates a dictionary from all attributes not starting with two underscores if no __all__":
            args = dict(a=1, b=2, c=3, d=4, e=5, _a=6, __ignored=7)
            module = imp.new_module('name')
            module.__dict__.update(args)
            self.file_faker.normalize_value(module) |should| equal_to({'a':1, 'b':2, 'c':3, 'd':4, 'e':5, '_a':6})

        it "works with an actual module rather than one I made on the fly for tests":
            this_dir = os.path.dirname(__file__)
            self.file_faker.normalize_value(stolen_vars) |should| equal_to(
                dict(a='a', b='b', c='c', one=1, two=2, three=3, _hidden='_hidden', this_dir=this_dir, os=os, steal=steal)
                )

    describe "Loading the module":
        before_each:
            self.fullname = "name.to.module"
            self.fake_path_from_fullname = fudge.Fake("path_from_fullname")
            self.file_faker = type("faker", (FileFaker, )
                , { 'value' : self.value
                  , 'path_from_fullname' : self.fake_path_from_fullname
                  }
                )(self.names, None)

        @fudge.patch('os.path.join')
        it "gets path and filename from path_from_fullname", fake_join:
            path = fudge.Fake("path")
            filename = fudge.Fake("filename")
            location = fudge.Fake("location")

            self.fake_path_from_fullname.expects_call().with_args(self.fullname).returns((path, filename))

            fake_join.expects_call().with_args(path, "%s.py" % filename).returns(location)
            self.file_faker.load_module(self.fullname).__file__ |should| be(location)

        @fudge.test
        it "populates the module with the values if self.values is a dictionary":
            values = {'a':'a', 'b':'b', 'c':'c'}
            self.file_faker.value = values
            self.fake_path_from_fullname.expects_call().returns(('', 'blah'))
            module = self.file_faker.load_module(self.fullname)

            len(module.__dict__.keys()) |should| be_greater_than(3)
            set(('a', 'b', 'c')) - set(module.__dict__.keys()) |should| equal_to(set())

            module.__dict__['a'] |should| equal_to('a')
            module.__dict__['b'] |should| equal_to('b')
            module.__dict__['c'] |should| equal_to('c')

        @fudge.test
        it "populates the module {value:value} if self.values is not a dictionary":
            self.fake_path_from_fullname.expects_call().returns(('', 'blah'))
            for val in (
                  0, 1, True, False, [], [1]
                , fudge.Fake("val"), type("object", (object, ), {}), type("object", (object, ), {})()
                , lambda : 2
                ):
                self.file_faker.value = val
                module = self.file_faker.load_module(self.fullname)
                module.__dict__['value'] |should| be(val)
