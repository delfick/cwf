# coding: spec

from should_dsl import should
from django.test import TestCase, override_settings
from django.contrib.sessions.middleware import SessionMiddleware

from cwf.sections.section import Section
from cwf.sections.values import Values
from cwf.views.menu import Menu

from django.http import HttpResponse

# Make the errors go away
be, equal_to = None, None

# Function to make a view that returns response
def make_view(response):
    def view(request, *args, **kwargs):
        res = HttpResponse(response)
        res.section = request.section
        return res
    return view

########################
###   URLS FOR TESTING
########################

    ########################
    ### Normal section

root = Section('').configure(promote_children=True, namespace='root')

root.add("one").configure(target=make_view("one"))

root.add("two").configure(target=make_view("two"))

three = root.add("three").configure(target=make_view("three"))
three.add("other").configure(target=make_view("three/other"))
three.add("three_child2").configure(target=make_view("three/three_child2"))

four = root.add("four").configure(target=make_view("four"))
four.add("jother").configure(target=make_view("four/other"))

five = root.add("five").configure(target=make_view("five"), promote_children=True)
six = five.add("six").configure(target=make_view("five/six"))
seven = five.add("seven").configure(target=make_view("five/seven"))

seven_v1 = seven.add('\d{4}').configure(''
    , match='year'
    , values=Values([2010, 2009], as_set=False)
    , target=make_view("five/seven/<year>")
    )
seven_v11 = seven_v1.add('\d+').configure(''
    , match='asdf'
    , values=Values([1])
    , target=make_view("five/seven/<year>/<asdf>")
    )

########################
###   TESTS
########################

@override_settings(ROOT_URLCONF=type("urlconf", (object, ), {"urlpatterns": root.patterns()}))
describe TestCase, "Menu":

    def get_info(self, path):
        res = self.client.get(path)
        res.status_code |should| be(200)

        request = res.request
        section = res.section

        menu = Menu(request, section)
        return request, section, menu

    def extract(self, infos, *args, **kwargs):
        look_at_selected = kwargs.get("look_at_selected", False)

        result = []
        for info in infos:
            item = []
            for arg in args:
                val = getattr(info, arg)
                if callable(val):
                    val = val()
                item.append(val)

            if look_at_selected and info.selected()[0]:
                item = [item, self.extract(info.children(), *args, **dict(look_at_selected=look_at_selected))]
            result.append(item)
        return result

    describe "Global Nav":
        it "returns a list of info objects for top level":
            request, section, menu = self.get_info('/three/other/')
            infos = list(menu.global_nav())

            extracted = self.extract(infos, 'alias')
            extracted |should| equal_to([['One'], ['Two'], ['Three'], ['Four'], ['Six'], ['Seven']])

        it "knows which top nav is selected":
            request, section, menu = self.get_info('/three/other/')
            infos = list(menu.global_nav())

            extracted = self.extract(infos, 'alias', 'selected')
            extracted |should| equal_to(
                [ ['One',   (False, [])]
                , ['Two',   (False, [])]
                , ['Three', (True,  ["other"])]
                , ['Four',  (False, [])]
                , ['Six',   (False, [])]
                , ['Seven', (False, [])]
                ]
            )

        it "knows url parts for each top nav":
            request, section, menu = self.get_info('/three/other/')
            infos = list(menu.global_nav())

            extracted = self.extract(infos, 'alias', 'url_parts')
            extracted |should| equal_to(
                [ ['One',   ['', 'one']]
                , ['Two',   ['', 'two']]
                , ['Three', ['', 'three']]
                , ['Four',  ['', 'four']]
                , ['Six',   ['', 'five', 'six']]
                , ['Seven', ['', 'five', 'seven']]
                ]
            )

    describe "Side Nav":
        it "returns a list of info objects for the selected top nav":
            request, section, menu = self.get_info('/three/other/')
            infos = list(menu.side_nav())

            extracted = self.extract(infos, 'alias', 'url_parts', 'selected')
            extracted |should| equal_to(
                [ ['Other',        ['', 'three', 'other'],        (True, [])]
                , ['Three_child2', ['', 'three', 'three_child2'], (False, [])]
                ]
            )

        it "can get urls for items in Value constructs":
            request, section, menu = self.get_info("/five/seven/2010/1/")
            infos = list(menu.side_nav())

            extracted = self.extract(infos, 'alias', 'url_parts', 'selected', look_at_selected=True)
            extracted |should| equal_to(
                [ [ [2010, ['', 'five', 'seven', 2010], (True, ['1'])]
                  , [ [ [1,  ['', 'five', 'seven', 2010, 1], (True, [])]
                      , []
                      ]
                    ]
                  ]
                , [ 2009, ['', 'five', 'seven', 2009], (False, [])]
                ]
            )
