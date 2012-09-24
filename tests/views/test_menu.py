# coding: spec

from cwf.views.menu import Menu

import fudge

describe "Menu":
    before_each:
        self.request = fudge.Fake("request")
        self.section = fudge.Fake("section")

    describe "Getting global menu":
        before_each:
            self.fake_navs_for = fudge.Fake("navs_for")
            self.menu = type("Menu", (Menu, ),
                { 'navs_for' : self.fake_navs_for
                }
            )(self.request, self.section)

        @fudge.test
        it "memoizes as self._global_nav":
            global_nav = fudge.Fake("global_nav")
            self.menu._global_nav = global_nav
            self.menu.global_nav() |should| be(global_nav)

        @fudge.test
        it "returns the navigation items for the menu_children of the root_ancestor of section":
            nav1 = fudge.Fake("nav1")
            nav2 = fudge.Fake("nav2")
            nav3 = fudge.Fake("nav3")
            navs = (nav1, nav2, nav3)

            menu_children = fudge.Fake("menu_children")
            root_ancestor = fudge.Fake("root_ancestor").has_attr(menu_children=menu_children)
            self.section.expects("root_ancestor").times_called(1).returns(root_ancestor)

            self.fake_navs_for.expects_call().with_args(menu_children).returns(navs)
            self.menu.global_nav() |should| equal_to([nav1, nav2, nav3])

            # Should be memoized
            self.menu.global_nav() |should| equal_to([nav1, nav2, nav3])

    describe "Getting side nav":
        before_each:
            self.selected_top_nav = fudge.Fake("selected_top_nav")
            self.menu = type("Menu", (Menu, ),
                { 'selected_top_nav' : self.selected_top_nav
                }
            )(self.request, self.section)

        @fudge.test
        it "memoizes as self._side_nav":
            side_nav = fudge.Fake("side_nav")
            self.menu._side_nav = side_nav
            self.menu.side_nav() |should| be(side_nav)

        @fudge.test
        it "returns children of the selected top nav":
            nav1 = fudge.Fake("nav1")
            nav2 = fudge.Fake("nav2")
            nav3 = fudge.Fake("nav3")
            navs = (nav1, nav2, nav3)

            self.selected_top_nav.expects("children").returns(navs)
            self.menu.side_nav() |should| equal_to([nav1, nav2, nav3])

        it "returns empty array if no selected top nav":
            self.menu.selected_top_nav = None
            self.menu.side_nav() |should| equal_to([])

    describe "Determining selected top nav":
        before_each:
            self.section1 = fudge.Fake("section1")
            self.section2 = fudge.Fake("section1")
            self.section3 = fudge.Fake("section1")

            self.fake_global_nav = fudge.Fake("global_nav")
            self.menu = type("Menu", (Menu, )
                , { 'global_nav' : self.fake_global_nav
                  }
              )(self.request, self.section)

        @fudge.test
        it "returns the first top nav to be selected":
            self.section1.expects("selected").returns([False, []])
            self.section2.expects("selected").returns([True, []])
            self.section3.expects("selected").returns([True, []])
            self.fake_global_nav.expects_call().times_called(1).returns([self.section1, self.section2, self.section3])
            self.menu.selected_top_nav |should| be(self.section2)

            # Value should be memoized, calling again won't make fudge complain
            self.menu.selected_top_nav |should| be(self.section2)

        @fudge.test
        it "returns None if no sections are selected":
            self.section1.expects("selected").returns([False, []])
            self.section2.expects("selected").returns([False, []])
            self.section3.expects("selected").returns([False, []])
            self.fake_global_nav.expects_call().times_called(1).returns([self.section1, self.section2, self.section3])
            self.menu.selected_top_nav |should| be(None)

            # Value should be memoized, calling again won't make fudge complain
            self.menu.selected_top_nav |should| be(None)

    describe "Getting path":
        it "Gets PATH_INFO from request and splits by slash":
            request = fudge.Fake('request').has_attr(META={'PATH_INFO' : 'blah/things'})
            Menu(request, None).path |should| equal_to(['blah', 'things'])

        it "strips trailing slashes":
            request = fudge.Fake('request').has_attr(META={'PATH_INFO' : 'blah/things///'})
            Menu(request, None).path |should| equal_to(['blah', 'things'])

        it "strips leading slashes":
            request = fudge.Fake('request').has_attr(META={'PATH_INFO' : '////blah/things'})
            Menu(request, None).path |should| equal_to(['blah', 'things'])

        it "strips leading and trailing slashes":
            request = fudge.Fake('request').has_attr(META={'PATH_INFO' : '////blah/things///'})
            Menu(request, None).path |should| equal_to(['blah', 'things'])

    describe "Generating function to act as children":
        before_each:
            self.parent = fudge.Fake("parent")
            self.fake_navs_for = fudge.Fake("navs_for")
            self.menu_children = fudge.Fake("menu_children")

            self.menu = type("Menu", (Menu, ), 
                { 'navs_for' : self.fake_navs_for
                }
            )(self.request, self.section)

        @fudge.test
        it "calls navs_for for the menu_children on specified section":
            navs = fudge.Fake("navs")
            self.section.menu_children = self.menu_children
            self.fake_navs_for.expects_call().with_args(self.menu_children, parent=self.parent).returns(navs)
            self.menu.children_function_for(self.section, self.parent)() |should| be(navs)

    describe "Getting navs for a list of sections":
        before_each:
            self.path = fudge.Fake("path")
            self.parent = fudge.Fake("parent")

            self.info1 = fudge.Fake("info1")
            self.info2 = fudge.Fake("info2")
            self.info3 = fudge.Fake("info3")

            self.has_children1 = fudge.Fake("has_children1")
            self.has_children2 = fudge.Fake("has_children2")

            self.section1 = fudge.Fake("section1").has_attr(has_children=self.has_children1)
            self.section2 = fudge.Fake("section2").has_attr(has_children=self.has_children2)
            self.include_as1 = fudge.Fake("include_as1")
            self.include_as2 = fudge.Fake("include_as2")

            self.item1 = fudge.Fake("item1").has_attr(section=self.section1, include_as=self.include_as1)
            self.item2 = fudge.Fake("item2").has_attr(section=self.section2, include_as=self.include_as2)
            self.items = [self.item1, self.item2]

            self.child_function1 = fudge.Fake("child_function1")
            self.child_function2 = fudge.Fake("child_function2")
            self.child_function3 = fudge.Fake("child_function3")
            self.fake_children_function_for = fudge.Fake("children_function_for")

            self.menu = type("Menu", (Menu, )
                , { 'path' : self.path
                  , 'children_function_for' : self.fake_children_function_for
                  }
                )(self.request, self.section)

        @fudge.test
        it "gets info using section master for each child using path and sets up children":
            master = (fudge.Fake("master").expects("get_info")
                .with_args(self.section1, self.include_as1, self.path, parent=self.parent).returns([self.info1])
                .next_call().with_args(self.section2, self.include_as2, self.path, parent=self.parent).returns([self.info2, self.info3])
                )

            # The children function allows us to inject into the infos logic from the menu
            # item2 has two infos so it gets called twice
            (self.fake_children_function_for.expects_call()
                .with_args(self.section1, self.info1).returns(self.child_function1)
                .next_call().with_args(self.section2, self.info2).returns(self.child_function2)
                .next_call().with_args(self.section2, self.info3).returns(self.child_function3)
                )

            # setup_children is how we inject menu logic
            self.info1.expects("setup_children").with_args(self.child_function1, self.has_children1)
            self.info2.expects("setup_children").with_args(self.child_function2, self.has_children2)
            self.info3.expects("setup_children").with_args(self.child_function3, self.has_children2)

            self.menu.master = master
            list(self.menu.navs_for(self.items, parent=self.parent)) |should| equal_to([self.info1, self.info2, self.info3])
