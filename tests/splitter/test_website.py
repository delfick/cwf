# coding: spec

from cwf.splitter.website import Website

import fudge

describe "Website":
    before_each:
        self.p1 = fudge.Fake("p1")
        self.p2 = fudge.Fake("p2")
        self.prefix = fudge.Fake("prefix")
        self.package = fudge.Fake("package")

    it "takes in package and parts":
        website = Website(self.package, self.p1, self.p2)
        website.parts |should| equal_to((self.p1, self.p2))
        website.package |should| be(self.package)

        # Default prefix to None
        website.prefix |should| be(None)

    it "takes prefix from kwargs":
        website = Website(self.package, prefix=self.prefix)
        website.parts |should| equal_to(())
        website.prefix |should| be(self.prefix)

    describe "Configuring website":
        before_each:
            self.urls = fudge.Fake("urls")
            self.models = fudge.Fake("models")
            self.fake_names_for = fudge.Fake("names_for")
            self.fake_load_admin = fudge.Fake("load_admin")

            self.website = type("website", (Website, )
                , { 'urls' : self.urls
                  , 'models' : self.models
                  , 'names_for' : self.fake_names_for
                  , 'load_admin' : self.fake_load_admin
                  }
                )(self.package)

        @fudge.patch('cwf.splitter.website.inject')
        it "injects urls and models and loads admin", fake_inject:
            called = []
            def call_with(num):
                return lambda *args: called.append(num)

            names_for_url = fudge.Fake("names_for_url")
            names_for_models = fudge.Fake("names_for_models")
            (self.fake_names_for.expects_call()
                .with_args('urls').returns(names_for_url)
                .next_call().with_args("models").returns(names_for_models)
                )

            # Inject used to put urls and models where they should go
            (fake_inject.expects_call()
                .with_args(self.urls, names_for_url).calls(call_with(1))
                .next_call().with_args(self.models, names_for_models).calls(call_with(2))
                )

            # The admin stuff is loaded
            self.fake_load_admin.expects_call().calls(call_with(3))

            # Start the configuring
            # And make sure the injects happend befored loading the admin
            self.website.configure()
            called |should| equal_to([1, 2, 3])

    describe "Getting Part config":
        it "returns self._partconfig[self.package]":
            config = fudge.Fake("config")
            website = Website(self.package)
            website._partconfig = {self.package : config}
            website.config |should| be(config)

        @fudge.patch("cwf.splitter.website.Parts")
        it "adds to existing _partconfig if package not in it", fakeParts:
            config = fudge.Fake("config")
            other_config = fudge.Fake("other_config")

            fakeParts.expects_call().with_args(self.package, self.p1, self.p2).returns(config)
            website = Website(self.package, self.p1, self.p2)
            website._partconfig = {'otherpackage' : other_config}
            website.config |should| equal_to(config)
            website._partconfig |should| equal_to({'otherpackage' : other_config, self.package : config})

        @fudge.patch("cwf.splitter.website.Parts")
        it "creates _partconfig if the website doesn't have it", fakeParts:
            config = fudge.Fake("config")
            other_config = fudge.Fake("other_config")

            fakeParts.expects_call().with_args(self.package, self.p1, self.p2).returns(config)
            website = Website(self.package, self.p1, self.p2)
            website |should_not| respond_to("_partconfig")
            website.config |should| equal_to(config)
            website._partconfig |should| equal_to({self.package : config})

    describe "Getting things from config":
        before_each:
            self.config = fudge.Fake("config")
            self.website = type("website", (Website, )
                , { 'config' : self.config
                  }
                )(self.package)

        describe "Loading admin":
            it "calls load_admin on the config":
                self.config.expects("load_admin")
                self.website.load_admin()

        describe "Getting models":
            it "returns config.models":
                models = fudge.Fake("models")
                self.config.expects("models").returns(models)
                self.website.models |should| be(models)

        describe "Getting urls":
            it "returns a function that calls config.urls":
                urls = fudge.Fake("urls")
                self.config.expects("urls").with_args(active_only=True).returns(urls)
                url_getter = self.website.urls
                url_getter() |should| be(urls)

    describe "getting names used to determine where to inject thigns":
        it "has <package>.<name>":
            name = fudge.Fake("name")
            names = Website(self.package).names_for(name)
            names |should| equal_to(["%s.%s" % (self.package, name)])

        it "also has <prefix>.<package>.<name> if self.prefix":
            name = fudge.Fake("name")
            names = Website(self.package, prefix=self.prefix).names_for(name)
            names |should| equal_to(
                ["%s.%s" % (self.package, name), "%s.%s.%s" % (self.prefix, self.package, name)]
                )
