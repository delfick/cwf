# coding: spec

from noseOfYeti.tokeniser.support import noy_sup_setUp
from should_dsl import should, should_not
from django.test import TestCase

from cwf.sections.errors import ConfigurationError
from cwf.sections.options import Options

import fudge

# Make the errors go away
be, equal_to, include, throw = None, None, None, None

describe TestCase, "Configuring Options":
    before_each:
        self.defaults = (
            # Conditionals
              ('admin', False)
            , ('active', True)
            , ('exists', True)
            , ('display', True)

            # View stuff
            , ('kls',  None)
            , ('module',  None)
            , ('target',  None)
            , ('redirect',  None)
            , ('extra_context',  None)

            # Url stuff
            , ('app_name', None)
            , ('namespace', None)

            # Pattern stuff
            , ('catch_all', False)

            # menu stuff
            , ('alias',  None)
            , ('match',  None)
            , ('values',  None)
            , ('needs_auth',  False)
            , ('promote_children',  False)
            , ('propogate_display', True)
            )

    it "has default values":
        options = Options()
        keys = [k for k, _ in self.defaults]
        existing = [k for k, v in options.__dict__.items() if
            not k.startswith("_") and not callable(v)
        ]

        # Make sure we haven't missed any keys
        sorted(keys) |should| equal_to(sorted(existing))

        # Check the values
        for k, v in self.defaults:
            getattr(options, k) |should| equal_to(v)

    describe "Setting things on the options":
        """
            Options has it's own methods for setting things
            These allow some sanity checks to be performed
        """
        before_each:
            self.specification = {
                  Options.set_view.im_func : ('kls', 'module', 'target', 'redirect', 'extra_context')
                , Options.set_menu.im_func : ('alias', 'match', 'values', 'needs_auth', 'propogate_display', 'promote_children')
                , Options.set_urlname.im_func : ('app_name', 'namespace')
                , Options.set_urlpattern.im_func : ('catch_all', )
                , Options.set_conditionals.im_func : ('admin', 'active', 'exists', 'display')
                }

        it "has a method that returns each setting function along with the arguments they require":
            used = []
            options = Options()
            for func, required in list(options.setters()):
                used.extend(required)
                self.specification |should| include(func.im_func)
                sorted(self.specification[func.im_func]) |should| equal_to(sorted(required))

            # Make sure the setters get everything
            sorted(used) |should| equal_to(sorted([k for k, _ in self.defaults]))

        it "doesn't set anything on options if any setter function is called without arguments":
            for setter, requirements in self.specification.items():
                options = fudge.Fake("options")
                properties = dict((requirement, fudge.Fake(requirement)) for requirement in requirements)
                for key, val in properties.items():
                    setattr(options, key, val)

                setter(options)
                for key, val in properties.items():
                    getattr(options, key) |should| be(val)

        describe "Setting everything":
            before_each:
                self.fake_setters = fudge.Fake("setters")
                self.options = type("Options", (Options, ), {'setters' : self.fake_setters})()

            @fudge.test
            it "looks at self.setters to determine what from kwargs to give to which setter":
                arg1 = fudge.Fake("arg1")
                arg2 = fudge.Fake("arg2")
                arg3 = fudge.Fake("arg3")
                arg4 = fudge.Fake("arg4")

                setter1 = fudge.Fake("setter1").expects_call().with_args(a=arg1, b=arg2)
                setter2 = fudge.Fake("setter2").expects_call().with_args(c=arg3, d=arg4)

                self.fake_setters.expects_call().returns([(setter1, ['a', 'b']), (setter2, ['c', 'd'])])
                self.options.set_everything(a=arg1, b=arg2, c=arg3, d=arg4)

            @fudge.test
            it "takes None as a valid argument to pass along":
                setter1 = fudge.Fake("setter1").expects_call().with_args(a=None, b=None)
                setter2 = fudge.Fake('setter2').expects_call().with_args(c=None)

                self.fake_setters.expects_call().returns([(setter1, ['a', 'b']), (setter2, ['c'])])
                self.options.set_everything(a=None, b=None, c=None)

            @fudge.test
            it "complains if setters asks for the same argument for multiple setters":
                arg1 = fudge.Fake("arg1")
                arg2 = fudge.Fake("arg2")
                arg3 = fudge.Fake("arg3")
                arg4 = fudge.Fake("arg4")

                setter1 = fudge.Fake("setter1").expects_call().with_args(a=arg1, b=arg2)
                setter2 = fudge.Fake('setter2')

                self.fake_setters.expects_call().returns([(setter1, ['a', 'b']), (setter2, ['a', 'd'])])
                caller = lambda: self.options.set_everything(a=arg1, b=arg2, c=arg3, d=arg4)
                caller |should| throw(ConfigurationError
                    , message="fake:setter2 takes argument (a) already taken elsewhere..."
                    )

            @fudge.test
            it "complains if any arguments aren't taken by a setter":
                arg1 = fudge.Fake("arg1")
                arg2 = fudge.Fake("arg2")
                arg3 = fudge.Fake("arg3")
                arg4 = fudge.Fake("arg4")
                arg5 = fudge.Fake("arg5")

                setter1 = fudge.Fake("setter1").expects_call().with_args(a=arg1, b=arg2)
                setter2 = fudge.Fake('setter2').expects_call().with_args(c=arg3)

                self.fake_setters.expects_call().returns([(setter1, ['a', 'b']), (setter2, ['c'])])
                caller = lambda: self.options.set_everything(a=arg1, b=arg2, c=arg3, d=arg4, e=arg5)
                caller |should| throw(ConfigurationError
                    , message="Arguments provided into set_everything that wasn't consumed ('d', 'e')"
                    )

        describe "Actually setting values":
            def check_expectation(self, setter, value, error=None, exclude=None):
                """
                    Call setter with a single keyword argument set to value for each keyword argument accepted
                    If error is specified, then we check that ConfigurationError with error as a message is risen
                    Otherwise we check value was set on the options
                """
                if exclude is None:
                    exclude = []
                requirements = self.specification[setter]
                if exclude:
                    requirements = [requirement for requirement in requirements if requirement not in exclude]

                old = fudge.Fake("old")
                options = Options()
                for requirement in requirements:
                    kwargs = {requirement:value}
                    setattr(options, requirement, old)

                    caller = lambda : setter(options, **kwargs)
                    if error:
                        caller |should| throw(ConfigurationError, message=error % {'name' : requirement})
                        getattr(options, requirement) |should| be(old)
                    else:
                        caller()
                        getattr(options, requirement) |should| be(value)

            def check_multiple_arguments(self, setter, kwargs, not_set):
                """
                    Check calling the setter with multiple arguments
                    Will make sure all arguments for the setter is being met via kwargs and not_set combined
                    kwargs is given to the setter and it is ensured that the values before are not those, and after they are
                    not_set is used to set values on options before, and it is checked they are unchanged after
                """
                setting = kwargs.keys() + not_set.keys()
                requirements = self.specification[setter]

                len(setting) |should| be(len(set(setting)))
                sorted(setting) |should| equal_to(sorted(requirements))

                options = Options()
                for k, v in not_set.items():
                    setattr(options, k, v)

                for k, v in kwargs.items():
                    getattr(options, k) |should_not| equal_to(v)

                setter(options, **kwargs)

                for k, v in kwargs.items():
                    getattr(options, k) |should| equal_to(v)

                for k, v in not_set.items():
                    getattr(options, k) |should| equal_to(v)

            describe "Setting conditionals":
                """These must be boolean or callable that takes a single argument"""
                before_each:
                    self.setter = Options.set_conditionals.im_func

                it "complains if any arguments are methods that take more than two parameters":
                    def func(self, request, other): pass
                    obj = type("obj", (object, ), {'method' : func})()
                    invalid = obj.method
                    self.check_expectation(self.setter, invalid
                        , error = "Conditionals as callables must only accept one argument, not 3 (['self', 'request', 'other'])"
                        )

                it "complains if any arguments are functions that take more than one parameters":
                    invalid = lambda one, two: 1
                    self.check_expectation(self.setter, invalid
                        , error = "Conditionals as callables must only accept one argument, not 2 (['one', 'two'])"
                        )

                it "complains if any argument is neither boolean or callable":
                    kls = type('obj', (object, ), {})
                    for val, typ in (
                          (0, int), (1, int)
                        , ([], list), ([1], list)
                        , ({}, dict), ({1:2}, dict)
                        , (kls(), kls)
                        , (None, type(None))
                        , ("", str)
                        , ('asdf', str)
                        ):
                        self.check_expectation(self.setter, val
                            , error = "Conditionals must be boolean or callable(request), not %s (%%(name)s=%s)" % (typ, val)
                            )

                it "sets argument on class if it's valid":
                    kls_func = lambda self, request: 1
                    kls = type('obj', (object, ), {'method' : kls_func})()
                    valid_method = kls.method
                    valid_func = lambda request: 1
                    for val in (False, True, valid_func, valid_method):
                        self.check_expectation(self.setter, val)

                it "works with multiple arguments":
                    kwargs = {'active' : False, 'admin' : True}
                    not_set = {'display': fudge.Fake('display'), 'exists' : fudge.Fake('exists')}
                    self.check_multiple_arguments(self.setter, kwargs=kwargs, not_set=not_set)

            describe "Setting View options":
                """These must be string, callable or None"""
                before_each:
                    self.setter = Options.set_view.im_func

                it "complains if any argument is neither string, callable or None":
                    kls = type('obj', (object, ), {})
                    for val, typ in (
                          (0, int), (1, int)
                        , (True, bool), (False, bool)
                        , ([], list), ([1], list)
                        , ({}, dict), ({1:2}, dict)
                        , (kls(), kls)
                        ):
                        self.check_expectation(self.setter, val
                            , error = "%%(name)s must be either a string or a callble, not %s (%s)" % (typ, val)
                            , exclude = 'extra_context'
                            )

                it "allows extra_context to be a dict":
                    options = Options()
                    self.setter(options, extra_context={})
                    assert True

                it "sets argument on class if it's valid":
                    kls_func = lambda self, request: 1
                    obj = type('obj', (object, ), {'method' : kls_func})()
                    for val in (None, "", "asdf", obj.method, fudge.Fake('callable'), lambda one: 1, lambda one, two: 2):
                        self.check_expectation(self.setter, val)

                it "works with multiple arguments":
                    kwargs = {'extra_context' : "", 'module' : fudge.Fake("callable"), 'target': lambda one: 1}
                    not_set = {'kls' : fudge.Fake('kls'), 'redirect' : fudge.Fake('redirect')}
                    self.check_multiple_arguments(self.setter, kwargs=kwargs, not_set=not_set)

            describe "Setting menu options":
                before_each:
                    self.setter = Options.set_menu.im_func

                it "doesn't care what values they are":
                    kls = type('obj', (object, ), {})
                    for val in (0, 1, [], [1], {}, {1:2}, kls, kls(), None, "", "asdf", lambda : 1, fudge.Fake("asdf")):
                        self.check_expectation(self.setter, val, exclude="values")

                it "complains if values doesn't have get_info method on it":
                    values = fudge.Fake("values")
                    caller = lambda : self.setter(Options(), values=values)
                    caller |should| throw(ConfigurationError
                        , message="Values must have a get_info method to get information from. fake:values does not"
                        )

                it "complains if values has get_info on it but it isn't callable":
                    for val in (0, 1, True, False, [], [1], {}, {1:2}):
                        obj = type("obj", (object, ), {'get_info' : val})()
                        caller = lambda : self.setter(Options(), values=obj)
                        caller |should| throw(ConfigurationError
                            , message="Values must have a get_info method to get information from. %s does not" % obj
                            )

                it "doesn't complain if values has a get_info method on it":
                    get_info = lambda : 1
                    obj = type("obj", (object, ), {'get_info' : get_info})()
                    options = Options()
                    self.setter(options, values=obj)
                    options.values |should| be(obj)

            describe "Setting url options":
                before_each:
                    self.setter = Options.set_urlname.im_func

                it "sets app_name and namespace":
                    app_name = fudge.Fake("app_name")
                    namespace = fudge.Fake("namespace")
                    options = Options()
                    self.setter(options, namespace=namespace, app_name=app_name)
                    options.app_name |should| be(app_name)
                    options.namespace |should| be(namespace)

            describe "Setting url pattern options":
                before_each:
                    self.setter = Options.set_urlpattern.im_func

                it "sets catch_all":
                    catch_all = fudge.Fake("catch_all")
                    options = Options()
                    self.setter(options, catch_all=catch_all)
                    options.catch_all |should| be(catch_all)
