# coding: spec

from src.splitter.parts import Parts

import fudge

describe "Parts Collection":
    before_each:
        self.p1 = fudge.Fake("p1")
        self.p2 = fudge.Fake("p2")
        self.p3 = fudge.Fake("p3")
        self.package = fudge.Fake("package")
        self.active_only = fudge.Fake("active_only")

    it "it takes in package and all the parts":
        parts = Parts(self.package, self.p1, self.p2, self.p3)
        parts.package |should| be(self.package)
        parts.parts |should| equal_to((self.p1, self.p2, self.p3))

    describe "Getting things":
        before_each:
            self.fake_each_part = fudge.Fake("each_part")
            self.fake_add_url_defaults = fudge.Fake("add_url_defaults")

            self.parts = type("Parts", (Parts, )
                , { 'each_part' : self.fake_each_part
                  , 'add_url_defaults' : self.fake_add_url_defaults
                  }
                )(self.package)

        describe "Loading admin":
            @fudge.test
            it "loads admin for each part":
                self.p1.expects("load").with_args("admin")
                self.p2.expects("load").with_args("admin")
                self.fake_each_part.expects_call().with_args(self.active_only).returns((self.p1, self.p2))
                self.parts.load_admin(self.active_only)

        describe "Getting models":
            @fudge.test
            it "loads models.__all__ and adds all to the dictionary":
                models = fudge.Fake("models")
                models.__all__ = ['one', 'two', 'three']
                models.one = 1
                models.two = 2
                models.three = 3
                self.fake_each_part.expects_call().with_args(self.active_only).returns((self.p1, ))
                self.p1.expects("load").with_args("models").returns(models)
                self.parts.models(self.active_only) |should| equal_to(dict(one=1, two=2, three=3))

            @fudge.test
            it "doesn't care about duplicate names":
                models1 = fudge.Fake("models")
                models1.__all__ = ['one', 'two', 'three']
                models1.one = 1
                models1.two = 2
                models1.three = 3

                models2 = fudge.Fake("models")
                models2.__all__ = ['one', 'four', 'five']
                models2.one = 6
                models2.four = 4
                models2.five = 5

                self.fake_each_part.expects_call().with_args(self.active_only).returns((self.p1, self.p2))
                self.p1.expects("load").with_args("models").returns(models1)
                self.p2.expects("load").with_args("models").returns(models2)
                self.parts.models(self.active_only) |should| equal_to(dict(one=6, two=2, three=3, four=4, five=5))

            @fudge.test
            it "ignores models without __all__":
                models1 = fudge.Fake("models")
                models1.__all__ = ['one', 'two', 'three']
                models1.one = 1
                models1.two = 2
                models1.three = 3

                models2 = fudge.Fake("models")
                models2.one = 6
                models2.four = 4
                models2.five = 5

                self.fake_each_part.expects_call().with_args(self.active_only).returns((self.p1, self.p2))
                self.p1.expects("load").with_args("models").returns(models1)
                self.p2.expects("load").with_args("models").returns(models2)
                self.parts.models(self.active_only) |should| equal_to(dict(one=1, two=2, three=3))

        describe "Getting urls":
            @fudge.test
            it "gets site and site.patterns as urlpatterns":
                site = fudge.Fake("site")
                patterns = fudge.Fake("patterns")

                fake_site = fudge.Fake("site").expects_call().with_args(self.package, self.active_only).returns(site)
                site.expects("patterns").returns(patterns)

                with fudge.patched_context(self.parts, 'site', fake_site):
                    self.parts.urls(self.active_only) |should| equal_to(dict(site=site, urlpatterns=patterns))

            @fudge.test
            it "adds default url objects from django if include_defaults is True":
                site = fudge.Fake("site")
                patterns = fudge.Fake("patterns")
                defaults = fudge.Fake("defaults")

                fake_site = fudge.Fake("site").expects_call().with_args(self.package, self.active_only).returns(site)
                site.expects("patterns").returns(patterns)

                def add_defaults(urls):
                    urls['defaults'] = defaults
                self.fake_add_url_defaults.expects_call().calls(add_defaults)

                with fudge.patched_context(self.parts, 'site', fake_site):
                    self.parts.urls(self.active_only, include_defaults=True) |should| equal_to(
                        dict(site=site, urlpatterns=patterns, defaults=defaults)
                    )

    describe "Getting imported parts":
        before_each:
            self.fake_import_paths = fudge.Fake("import_paths")
            self.parts = type("parts", (Parts, )
                , { 'import_parts' : self.fake_import_paths
                  }
                )(self.package)

        @fudge.test
        it "calls import_paths and returns self.parts the first time":
            parts = fudge.Fake("parts")
            self.parts.parts = parts

            self.fake_import_paths.expects_call()
            self.parts.imported_parts |should| be(parts)

        @fudge.test
        it "doesn't calls import_paths on subsequent calls but still returns self.parts":
            parts = fudge.Fake("parts")
            self.parts.parts = parts

            self.fake_import_paths.expects_call().times_called(1)
            self.parts.imported_parts |should| be(parts)
            self.parts.imported_parts |should| be(parts)
            self.parts.imported_parts |should| be(parts)

    describe "Itering all the parts":
        before_each:
            self.parts = Parts(self.package)

        @fudge.test
        it "yields all the parts if active_only is False":
            imported_parts = [self.p1, self.p2, self.p3]
            self.p1.has_attr(active=False)
            self.p2.has_attr(active=True)
            self.p3.has_attr(active=True)
            with fudge.patched_context(self.parts, 'imported_parts', imported_parts):
                list(self.parts.each_part(active_only=False)) |should| equal_to([self.p1, self.p2, self.p3])

        @fudge.test
        it "yields only active parts if active_only is True":
            imported_parts = [self.p1, self.p2, self.p3]
            self.p1.has_attr(active=False)
            self.p2.has_attr(active=True)
            self.p3.has_attr(active=True)
            with fudge.patched_context(self.parts, 'imported_parts', imported_parts):
                list(self.parts.each_part(active_only=True)) |should| equal_to([self.p2, self.p3])
    
    describe "Importing parts":
        before_each:
            self.parts = Parts(self.package)

        @fudge.test
        it "Imports all the parts":
            parts = [self.p1, self.p2, self.p3]
            self.parts.parts = parts
            self.p1.expects("do_import").with_args(self.package)
            self.p2.expects("do_import").with_args(self.package)
            self.p3.expects("do_import").with_args(self.package)
            self.parts.import_parts()

    describe "Getting a site object":
        before_each:
            self.urls1 = fudge.Fake("urls1")
            self.urls2 = fudge.Fake("urls2")
            self.urls3 = fudge.Fake("urls2")

            self.section1 = fudge.Fake("section1")
            self.section2 = fudge.Fake("section2")
            self.section3 = fudge.Fake("section2")

            self.name = fudge.Fake("name")
            self.fake_each_part = fudge.Fake("each_part")
            self.parts = type("parts", (Parts, ), {'each_part' : self.fake_each_part})(self.package)

        @fudge.patch("src.splitter.parts.Section")
        it "creates a Section and adds all urls.section to it", fakeSection:
            site = fudge.Fake("site")
            self.fake_each_part.expects_call().with_args(self.active_only).returns([self.p1, self.p2, self.p3])

            self.p1.expects("load").with_args("urls").returns(self.urls1.has_attr(section=self.section1))
            self.p2.expects("load").with_args("urls").returns(self.urls2.has_attr(section=self.section2))
            self.p3.expects("load").with_args("urls").returns(self.urls3.has_attr(section=self.section3))

            self.p1.has_attr(kwargs=dict(one=1, two=2))
            self.p2.has_attr(kwargs=dict(three=3, four=4))
            self.p3.has_attr(kwargs=dict(five=5, six=6))

            (site.expects("add")
                .with_args(self.section1, one=1, two=2)
                .next_call().with_args(self.section2, three=3, four=4)
                .next_call().with_args(self.section3, five=5, six=6)
                )

            fakeSection.expects_call().with_args(self.name, promote_children=True).returns(site)
            self.parts.site(self.name, self.active_only) |should| be(site)

        @fudge.patch("src.splitter.parts.Section")
        it "ignores parts that don't have urls or a section", fakeSection:
            site = fudge.Fake("site")
            self.fake_each_part.expects_call().with_args(self.active_only).returns([self.p1, self.p2, self.p3])

            self.p1.expects("load").with_args("urls").returns(None)
            self.p2.expects("load").with_args("urls").returns(self.urls2)
            self.p3.expects("load").with_args("urls").returns(self.urls3.has_attr(section=self.section3))

            self.p1.has_attr(kwargs=dict(one=1, two=2))
            self.p2.has_attr(kwargs=dict(three=3, four=4))
            self.p3.has_attr(kwargs=dict(five=5, six=6))

            # Only gets called with section3
            # Because p1 doesn't have urls
            # And p2 doesn't have urls.section
            site.expects("add").with_args(self.section3, five=5, six=6)
            fakeSection.expects_call().with_args(self.name, promote_children=True).returns(site)
            self.parts.site(self.name, self.active_only) |should| be(site)

    describe "Adding url defaults":
        @fudge.patch("django.conf.urls.defaults")
        it "adds all non private things from django.conf.urls.defaults to the provided dictionary", fake_defaults:
            fake_defaults.a = 'a'
            fake_defaults.b = 'b'
            fake_defaults._c = 'c'
            fake_defaults._d = 'd'
            fake_defaults.__name__ = 'defaults'

            fake_dir = fudge.Fake("dir").expects_call().with_args(fake_defaults).returns(['a', 'b', '_c', '_d', '__name__'])

            urls = {}
            with fudge.patched_context("__builtin__", "dir", fake_dir):
                Parts(self.package).add_url_defaults(urls)
            urls |should| equal_to(dict(a='a', b='b'))
