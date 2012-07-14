# coding: spec

from tests import extra_matchers

from src.sections.section import Section
from src.sections.values import Values
from src.views.menu import Menu

import fudge

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

section = Section('', name="templatetest")
section.first().configure(alias="Home")

    ########################
    ###   SECTION1

sect1 = section.add('one').configure(target=make_view("/one/"))
sect1_some = sect1.add('some').configure(alias='blah', target=make_view("/one/some/"))
sect1_blah = sect1.add('\w+').configure(
      match = 'blah'
    , target=make_view("/one/<blah>/")
    , values = Values(
        lambda (r, pu, p) : ['2', '1', '3']
      , lambda (r, pu, p), value : ('_%s' % value, '%s_' % value)
      , sorter = True
      )
    )

    ########################
    ###   SECTION2

sect2 = section.add('2').configure(alias='two')
sect2_first = sect2.first().configure(alias='meh', target=make_view("/2/"))

sect2_1 = sect2.add('1').configure(target=make_view("/2/1/"))
sect2_1_1 = sect2_1.add('2').configure(active=False, target=make_view("/2/2/"))
sect2_1_2 = sect2_1.add('3').configure(target=make_view("/2/3/"))
sect2_1_2_1 = sect2_1_2.add('4').configure(target=make_view("/2/4/"))

    ########################
    ###   SECTION3

sect3 = section.add('3').configure(display=False, target=make_view("/3/"))
sect3.add('test1').configure(target=make_view("/3/test1"))

    ########################
    ###   SECTION4

sect4 = section.add('4').configure(target=make_view("/4/"), display=False, propogate_display=False)
sect4_1 = sect4.add('this').configure(target=make_view("/4/this/"))
sect4_2 = sect4.add('needs').configure(target=make_view("/4/needs/"))
sect4_4 = sect4.add('more').configure(target=make_view("/4/more/"))
sect4_5 = sect4.add('creativity').configure(target=make_view("/4/creativity/"))

sect4_2_1 = sect4_2.add('a').configure(target=make_view("/4/needs/a/"))
sect4_2_2 = sect4_2.add('path').configure(target=make_view("/4/needs/path/"))
sect4_2_3 = sect4_2.add('going').configure(target=make_view("/4/needs/going/"))
sect4_2_4 = sect4_2.add('somewhere').configure(target=make_view("/4/needs/somewhere/"))

sect4_2_2_1 = sect4_2_2.add('\w+').configure(
      values = Values(['1', '2', '3'], as_set=False)
    , target = make_view("/4/needs/path/\w+/")
    )

sect4_2_2_1_1 = sect4_2_2_1.add('meh').configure(target=make_view("/4/needs/path/\w+/meh/"))

sect4_4_1 = sect4_4.add('test').configure(target=make_view("/4/more/test/"))
sect4_4_2 = sect4_4.add('blah').configure(target=make_view("/4/more/blah/"))

########################
###   TESTS
########################

describe "Rendering the menu":
    before_each:
        self.section = section
        self.request = fudge.Fake("request")
        self.request.user = fudge.Fake("user")

    def lookat_global(self, section, path, desired):
        menu = type("Menu", (Menu, ), {'path' : path.split('/')})(self.request, section)
        menu.global_nav() |should| render_as(desired)
            
    it 'should make a global menu with base selected':
        self.lookat_global(self.section, "/", """
            <ul>
                <li class="selected"><a href="/">Home</a></li>
                <li><a href="/one">One</a></li>
                <li><a href="/2">two</a></li>
            </ul>
        """)
    
    it 'should make a global menu with section other than base selected':
        self.lookat_global(self.section, "/one/", """
            <ul>
                <li><a href="/">Home</a></li>
                <li class="selected"><a href="/one">One</a></li>
                <li><a href="/2">two</a></li>
            </ul>
            """)
