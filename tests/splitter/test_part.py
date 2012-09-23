# coding: spec

from cwf.splitter.parts import Part

import fudge
import types

describe "Part":
    it "gets name, active and kwargs":
        name = fudge.Fake("name")
        active = fudge.Fake("active")
        kwargs = dict(one=1, two=2)

        part = Part(name, active, **kwargs)
        part.name |should| be(name)
        part.active |should| be(active)
        part.kwargs |should| equal_to(dict(one=1, two=2))

    it "adds include_as to kwargs if name is a string and kwargs doesn't have include_as":
        name = "to include as"
        part = Part(name)
        part.kwargs['include_as'] |should| equal_to(name)

    it "doesn't add include_as if 'first' is in kwargs and truthy":
        name = "to include as"
        part = Part(name, first=True)
        part.kwargs |should_not| contain('include_as')

    it "leaves include_as alone if already in kwargs":
        name = "to include as"
        active = fudge.Fake("active")
        include_as = fudge.Fake("include_as")

        part = Part(name, active, include_as=include_as)
        part.kwargs['include_as'] |should| equal_to(include_as)

    describe "doing an import":
        before_each:
            self.name = fudge.Fake("name")
            self.active = fudge.Fake("active")
            self.package = fudge.Fake("package")

        it "sets self.pkg to self.name if not a string":
            part = Part(self.name, self.active)
            part |should_not| respond_to("pkg")
            part.do_import(self.package)
            part.pkg |should| be(self.name)

        it "sets self.pkg to package.<self.name> if package is not a string":
            pkg = fudge.Fake("pkg")
            name = "thename"
            self.package.has_attr(thename=pkg)

            part = Part(name, self.active)
            part |should_not| respond_to("pkg")
            part.do_import(self.package)
            part.pkg |should| be(pkg)

        it "does from package import name as self.pkg if package and name are both strings":
            pkg = fudge.Fake("pkg")
            lcls = fudge.Fake("lcls")
            glbls = fudge.Fake('glbls')
            imported = fudge.Fake("imported")

            name = "stuff"
            package = "things.blah"
            imported.has_attr(stuff=pkg)
            fake_import = fudge.Fake("import").expects_call().with_args(package, glbls, lcls, [name], -1).returns(imported)

            part = Part(name, self.active)
            with fudge.patched_context("__builtin__", "globals", lambda : glbls):
                with fudge.patched_context("__builtin__", "locals", lambda : lcls):
                    with fudge.patched_context("__builtin__", "__import__", fake_import):
                        part |should_not| respond_to("pkg")
                        part.do_import(package)

            part.pkg |should| be(pkg)

    describe "Loading package from self.pkg":
        it "gets it straight from package if already there":
            part = Part("part1", True)
            part.do_import("tests.splitter.website")

            part.pkg |should| respond_to("things")

            # Want to make sure it doesn't need import again to get the thing
            fake_import = fudge.Fake("__import__")
            with fudge.patched_context("__builtin__", "__import__", fake_import):
                thing = part.load("things")
                thing |should| equal_to("things")

        it "imports it from package if not already there":
            part = Part("part1", True)
            part.do_import("tests.splitter.website")
            not_in_package = part.load("not_in_package")
            type(not_in_package) |should| be(types.ModuleType)
            not_in_package.not_in_package |should| equal_to("not_in_package")

        it "ignores import error if it can't find the module to be imported":
            part2 = Part("part2", True)
            part2.do_import("tests.splitter.website")
            not_there = part2.load("not_there")
            not_there |should| be(None)
        
        it "raises errors if importing a module that has problems":
            part1 = Part("part1", True)
            part1.do_import("tests.splitter.website")
            with self.assertRaises(SyntaxError):
                part1.load("syntax_error")

        it "successfully imports from module if there and has no errors on import":
            part2 = Part("part2", True)
            part2.do_import("tests.splitter.website")
            correct = part2.load("correct")
            from tests.splitter.website.part2 import correct as real_correct
            correct |should| be(real_correct)
