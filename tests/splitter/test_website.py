# coding: spec

from src.splitter.website import Website

import fudge

describe "Website":
    before_each:
        self.p1 = fudge.Fake("p1")
        self.p2 = fudge.Fake("p2")
        self.prefix = fudge.Fake("prefix")
        self.package = fudge.Fake("package")
        self.settings = fudge.Fake("settings")
        self.include_default_urls = fudge.Fake("include_default_urls")

    it "takes in settings, package and parts":
        website = Website(self.settings, self.package, self.p1, self.p2)
        website.parts |should| equal_to((self.p1, self.p2))
        website.package |should| be(self.package)
        website.settings |should| be(self.settings)

        # Default prefix to None
        # And include_defaults_urls to False
        website.prefix |should| be(None)
        website.include_default_urls |should| be(False)

    it "takes prefix and include_default_urls from kwargs":
        website = Website(self.settings, self.package, prefix=self.prefix, include_default_urls=self.include_default_urls)
        website.parts |should| equal_to(())
        website.prefix |should| be(self.prefix)
        website.include_default_urls |should| be(self.include_default_urls)

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
                )(self.settings, self.package)

        @fudge.patch('src.splitter.website.inject')
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
        it "returns settings.PARTCONFIG[self.package]":
            config = fudge.Fake("config")
            self.settings.PARTCONFIG = {self.package : config}
            website = Website(self.settings, self.package)
            website.config |should| be(config)

        @fudge.patch("src.splitter.website.Parts")
        it "adds to existing PARTCONFIG if package not in it", fakeParts:
            config = fudge.Fake("config")
            other_config = fudge.Fake("other_config")
            self.settings.PARTCONFIG = {'otherpackage' : other_config}

            fakeParts.expects_call().with_args(self.package, self.p1, self.p2).returns(config)
            website = Website(self.settings, self.package, self.p1, self.p2)
            website.config |should| equal_to(config)
            self.settings.PARTCONFIG |should| equal_to({'otherpackage' : other_config, self.package : config})

        @fudge.patch("src.splitter.website.Parts")
        it "creates PARTCONFIG if settings doesn't have it", fakeParts:
            config = fudge.Fake("config")
            other_config = fudge.Fake("other_config")
            self.settings |should_not| respond_to("PARTCONFIG")

            fakeParts.expects_call().with_args(self.package, self.p1, self.p2).returns(config)
            website = Website(self.settings, self.package, self.p1, self.p2)
            website.config |should| equal_to(config)
            self.settings.PARTCONFIG |should| equal_to({self.package : config})

    describe "Getting things from config":
        before_each:
            self.config = fudge.Fake("config")
            self.website = type("website", (Website, )
                , { 'config' : self.config
                  }
                )(self.settings, self.package, include_default_urls=self.include_default_urls)

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
            it "returns a function that calls config.urls with self.include_default_urls":
                urls = fudge.Fake("urls")
                self.config.expects("urls").with_args(include_defaults=self.include_default_urls).returns(urls)
                url_getter = self.website.urls
                url_getter() |should| be(urls)

    describe "getting names used to determine where to inject thigns":
        it "has <package>.<name>":
            name = fudge.Fake("name")
            names = Website(self.settings, self.package).names_for(name)
            names |should| equal_to(["%s.%s" % (self.package, name)])

        it "also has <prefix>.<package>.<name> if self.prefix":
            name = fudge.Fake("name")
            names = Website(self.settings, self.package, prefix=self.prefix).names_for(name)
            names |should| equal_to(
                ["%s.%s" % (self.package, name), "%s.%s.%s" % (self.prefix, self.package, name)]
                )
