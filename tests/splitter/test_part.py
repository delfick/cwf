# coding: spec

from cwf.splitter.parts import Part

import fudge

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
        active = fudge.Fake("active")
        part = Part(name, active)
        part.kwargs['include_as'] |should| equal_to(name)

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
        before_each:
            self.pkg = fudge.Fake("pgk")
            self.obj = fudge.Fake("obj")
            self.name = fudge.Fake("name")
            self.active = fudge.Fake("active")
            self.pkg_name = fudge.Fake("pkg_name")

            self.pkg.__name__ = self.pkg_name
            self.part = type("parts", (Part, ), {'pkg' : self.pkg})(self.name, self.active)

        it "gets it straight from package if already there":
            self.pkg.blah = self.obj
            self.part.load('blah') |should| be(self.obj)

        @fudge.test
        it "imports it from package if not already there":
            lcls = fudge.Fake("lcls")
            glbls = fudge.Fake('glbls')
            def do_import(*args):
                self.pkg.blah = self.obj

            fake_import = (fudge.Fake("import").expects_call()
                .with_args(self.pkg_name, glbls, lcls, ['blah'], -1).calls(do_import)
                )

            with fudge.patched_context("__builtin__", "globals", lambda : glbls):
                with fudge.patched_context("__builtin__", "locals", lambda : lcls):
                    with fudge.patched_context("__builtin__", "__import__", fake_import):
                        self.part.load('blah') |should| be(self.obj)

        it "ignores import error if it needs to import":
            lcls = fudge.Fake("lcls")
            glbls = fudge.Fake('glbls')
            fake_import = (fudge.Fake("import").expects_call()
                .with_args(self.pkg_name, glbls, lcls, ['blah'], -1).raises(ImportError)
                )

            with fudge.patched_context("__builtin__", "globals", lambda : glbls):
                with fudge.patched_context("__builtin__", "locals", lambda : lcls):
                    with fudge.patched_context("__builtin__", "__import__", fake_import):
                        self.part.load('blah') |should| be(None)
        
        it "works on an actual package":
            part1 = Part("part1", True)
            part1.do_import("tests.splitter.website")
            with self.assertRaises(SyntaxError):
                part1.load("syntax_error")
            part1.load("things") |should| be("things")

            part2 = Part("part2", True)
            part2.do_import("tests.splitter.website")
            correct = part2.load("correct")
            from tests.splitter.website.part2 import correct as real_correct
            correct |should| be(real_correct)
