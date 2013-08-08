# coding: spec

from cwf.admin.buttons import ButtonWrap

from contextlib import contextmanager
import fudge

describe "ButtonWrap":
    before_each:
        self.button = fudge.Fake("button")
        self.request = fudge.Fake("request")
        self.original = fudge.Fake("original")

        self.wrapper = ButtonWrap(self.button, self.request, self.original)

    it "puts button, request and original as private attributes on wrapper":
        self.wrapper._button |should| be(self.button)
        self.wrapper._request |should| be(self.request)
        self.wrapper._original |should| be(self.original)

    describe "Delegation":
        it "delegates attribute access to the button":
            things = fudge.Fake("things")
            self.button.has_attr(things=things)
            self.wrapper.things |should| be(things)

        @fudge.test
        it "defaults to wrapper over button if attribute on wrapper":
            button_things = fudge.Fake("button_things")

            wrapper_things = fudge.Fake("wrapper_things")
            wrapper_things_called = fudge.Fake("wrapper_things_called").expects_call().returns(wrapper_things)

            self.button.has_attr(things=button_things, prop_things=button_things)
            wrapper = type("wrapper", (ButtonWrap, )
                , {'things' : wrapper_things
                  , 'prop_things' : property(wrapper_things_called)
                  }
                )(self.button, self.request, self.original)

            wrapper.things |should| be(wrapper_things)
            wrapper.prop_things |should| be(wrapper_things)
            self.button.things |should| be(button_things)

        it "defaults to wrapper over button if attribute starts with underscore":
            self.wrapper.__class__ |should| be(ButtonWrap)
            self.button.__class__ |should| be(fudge.Fake)

        it "gets from wrapper if button doesn't have attribute":
            other = fudge.Fake("other")

            self.button |should_not| respond_to("other")
            wrapper = type("wrapper", (ButtonWrap, )
                , { 'other' : other
                  }
                )(self.button, self.request, self.original)

            wrapper.other |should| be(other)

    describe "Determining if button can be shown":
        @contextmanager
        def specified_values(self, display, has_permissions, noshow):
            wrapper = type("wrap", (ButtonWrap, )
                , { 'noshow' : noshow
                  , 'display' : display
                  , 'has_permissions' : has_permissions
                  }
                )(self.button, self.request, self.original)
            yield wrapper

        it "says no when noshow":
            spec = [
                  (False, False)
                , (False, True)
                , (True, False)
                ]

            for display, has_permissions in spec:
                with self.specified_values(display=display, has_permissions=has_permissions, noshow=True) as wrapper:
                    wrapper.show |should| be(False)

        it "says no if not noshow and can't be displayed or has no permissions":
            spec = [
                  (False, False)
                , (False, True)
                , (True, False)
                ]

            for display, has_permissions in spec:
                with self.specified_values(display=display, has_permissions=has_permissions, noshow=False) as wrapper:
                    wrapper.show |should| be(False)

        it "says yes if not noshow and can be displayed and has permissions":
            with self.specified_values(display=True, has_permissions=True, noshow=False) as wrapper:
                wrapper.show |should| be(True)

    describe "Determining if should not show":
        it "returns if not button.condition":
            self.button.has_attr(condition=False)
            self.wrapper.noshow |should| be(False)

            self.button.has_attr(condition=False)
            self.wrapper.noshow |should| be(False)

        it "calls button.condition with button and original if callable":
            condition = (fudge.Fake("condition").expects_call()
                .with_args(self.button, self.original).returns(True)
                .next_call().with_args(self.button, self.original).returns(False)
                )
            self.button.has_attr(condition=condition)

            # First time returns False
            self.wrapper.noshow |should| be(True)

            # Second time returns True
            self.wrapper.noshow |should| be(False)

    describe "Determining if button has permissions":
        before_each:
            self.fake_has_auth = fudge.Fake("has_auth")
            self.wrapper = type("Wrap", (ButtonWrap, )
                , { 'has_auth' : self.fake_has_auth
                  }
                )(self.button, self.request, self.original)

        @fudge.test
        it "returns True if user is super user":
            user = fudge.Fake("user").has_attr(is_superuser=True)
            spec = [
                  (False, False)
                , (True, True)
                , (True, False)
                , (False, True)
                ]

            self.request.has_attr(user=user)
            for needs_auth, need_super_user in spec:
                self.wrapper.needs_auth = needs_auth
                self.wrapper.need_super_user = need_super_user
                self.wrapper.has_permissions |should| be(True)

        @fudge.test
        it "returns False if wrapper needs super user and request.user is not a superuser":
            user = fudge.Fake("user").has_attr(is_superuser=False)
            self.request.has_attr(user=user)
            self.wrapper.need_super_user = True
            self.wrapper.has_permissions |should| be(False)

        @fudge.test
        it "returns True if wrapper doesn't need authentication":
            user = fudge.Fake("user").has_attr(is_superuser=False)
            self.request.has_attr(user=user)

            self.wrapper.needs_auth = False
            self.wrapper.need_super_user = False
            self.wrapper.has_permissions |should| be(True)

        @fudge.test
        it "returns True if wrapper doesn't need authentication unless needs super user":
            user = fudge.Fake("user").has_attr(is_superuser=False)
            self.request.has_attr(user=user)

            self.wrapper.needs_auth = False
            self.wrapper.need_super_user = True
            self.wrapper.has_permissions |should| be(False)

        @fudge.test
        it "returns whether user has specified auth":
            user = fudge.Fake("user").has_attr(is_superuser=False)
            result = fudge.Fake("result")
            needs_auth = fudge.Fake("needs_auth")

            self.request.has_attr(user=user)
            self.fake_has_auth.expects_call().with_args(user, needs_auth).returns(result)

            self.wrapper.needs_auth = needs_auth
            self.wrapper.need_super_user = False
            self.wrapper.has_permissions |should| be(result)

    describe "Determining if user has specified auth":
        @fudge.test
        it "auth is a boolean, return wheter user.is_authenticated()":
            authenticated = fudge.Fake("authenticated")
            user = fudge.Fake("user").expects("is_authenticated").returns(authenticated)

            self.request.has_attr(user=user)
            self.wrapper.has_auth(user, True) |should| be(authenticated)

        @fudge.test
        it "returns wheter user.has_perm(auth) if auth is not a list or tuple":
            auth = fudge.Fake("auth")
            authenticated = fudge.Fake("authenticated")

            user = (fudge.Fake("user").expects("has_perm")
                .with_args(auth).returns(True)
                .next_call().with_args(auth).returns(False)
                )

            self.request.has_attr(user=user)

            # First time has_perm says yes
            self.wrapper.has_auth(user, auth) |should| be(True)

            # Second time has_perm says no
            self.wrapper.has_auth(user, auth) |should| be(False)

        @fudge.test
        it "returns no user doesn't have any of the permissions specified by auth":
            auth = [1, 2, 3, 4, 5, 6]
            def has_perm(perm):
                if perm == 3:
                    return False
                return True
            user = fudge.Fake("user").expects("has_perm").calls(has_perm)
            self.request.has_attr(user=user)

            self.wrapper.has_auth(user, auth) |should| be(False)

        @fudge.test
        it "returns yes if user has all permissions specified by auth":
            auth = [1, 2, 3, 4, 5, 6]
            user = fudge.Fake("user").expects("has_perm").times_called(len(auth)).returns(True)
            self.request.has_attr(user=user)

            self.wrapper.has_auth(user, auth) |should| be(True)
