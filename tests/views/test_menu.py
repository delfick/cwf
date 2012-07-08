# coding: spec

from src.sections.section import Section
from src.views.menu import Menu

from django.http import HttpResponse

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

root = Section('root').configure(promote_children=True)

root.add("one").configure(target=make_view("one"))

root.add("two").configure(target=make_view("two"))

three = root.add("three").configure(target=make_view("three"))
three.add("other").configure(target=make_view("three/other"))

four = root.add("four").configure(target=make_view("four"))
four.add("jother").configure(target=make_view("four/other"))

five = root.add("five").configure(target=make_view("five"), promote_children=True)
six = five.add("six").configure(target=make_view("five/six"))
seven = five.add("seven").configure(target=make_view("five/seven"))

########################
###   TESTS
########################

describe "Menu":
    urls = root.patterns()

    def get_request_and_section(self, path):
        res = self.client.get(path)
        res.status_code |should| be(200)
        return res.request, res.section

    def extract(self, infos, *args):
        result = []
        for info in infos:
            item = []
            for arg in args:
                val = getattr(info, arg)
                if callable(val):
                    val = val()
                item.append(val)
            result.append(item)
        return result

    describe "Getting global menu":
        it "returns info objects representing global nav":
            request, section = self.get_request_and_section('/three/other/')
            menu = Menu(request, section)
            infos = list(menu.global_nav())

            extracted = self.extract(infos, 'alias')
            extracted |should| equal_to([['One'], ['Two'], ['Three'], ['Four'], ['Six'], ['Seven']])

        it "sets selected on the selected top nav":
            request, section = self.get_request_and_section('/three/other/')
            menu = Menu(request, section)
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
            request, section = self.get_request_and_section('/three/other/')
            menu = Menu(request, section)
            infos = list(menu.global_nav())

            extracted = self.extract(infos, 'alias', 'url_parts')
            extracted |should| equal_to(
                [ ['One',   ['', 'one']]
                , ['Two',   ['', 'two']]
                , ['Three', ['', 'three']]
                , ['Four',  ['', 'four']]
                , ['Six',   ['', 'six']]
                , ['Seven', ['', 'seven']]
                ]
            )
