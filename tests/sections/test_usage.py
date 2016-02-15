# coding: spec

from should_dsl import should
from django.test import TestCase
from django.test.utils import override_settings

from noseOfYeti.tokeniser.containers import acceptable
from django.http import HttpResponse

from cwf.sections.section import Section

# Make the errors go away
equal_to = None

# Function to make a view that returns response
def make_view(response):
    def view(request):
        return HttpResponse(response)
    return view

########################
###   URLS FOR TESTING
########################

    ########################
    ### Normal section

section = Section('base')

# Add with no children
add0 = section.add('add0').configure(target=make_view('/add0/'))

# Add with children, no first
add1 = section.add('add1').configure(target=make_view('/add1/'))
add12 = add1.add('add12').configure(target=make_view('/add1/add12/'))
add123 = add12.add('add123').configure(target=make_view('/add1/add12/add123/'))

# Add with no target and no children
add_nt0 = section.add('add_nt0')

# Add with no target and children
add_nt1 = section.add('add_nt1')
add_nt12 = add_nt1.add('add_nt12').configure(target=make_view('/add_nt1/add_nt12/'))

# Add with no target and no children but a first
add_ntf0 = section.add('add_ntf0')
add_ntf0.first().configure(target=make_view('/add_ntf0/'))

# Add with a redirect
add_r0 = section.add('add_r0').configure(redirect="add1")

# Add with promoted children
add_ignored = section.add("ignored").configure(promote_children=True)
add_ignored.add("one").configure(target=make_view("/ignored/one/"))
add_ignored.add("two").configure(target=make_view("/ignored/two/"))

    ########################
    ### Foster section

section_foster = Section('foster')
section_foster.adopt(section, clone=True)

    ########################
    ### Merger section

section_merger = Section('merged')
section_merger.add("other").configure(target=make_view('/other/'))
section_merger.merge(section)

########################
###   TEST HELPER
########################

class SectionTesterBase(TestCase):
    """
        Helper class to bring out common things to test
        Means testing the cloning of sections and adding sections as children to others
        Is simple to do later on
    """
    def ensure(self, url, check):
        """
            Ensure that going to a url gets back content equal to the url
            This is done by defining each url to explicitly return that url
        """
        ret = self.client.get(url)
        ret.status_code |should| equal_to(200)
        ret.content |should| equal_to(check)

    def refute(self, url):
        """
            Ensure that going to a url gets back a 404
        """
        ret = self.client.get(url)
        ret.status_code |should| equal_to(404)

    def redirects(self, url, destination):
        """
            Ensure that going to a url gets back a 301 Permanent Redirect
        """
        print(url)
        ret = self.client.get(url)
        ret.status_code |should| equal_to(301)
        dict(ret.items())['Location'] |should| equal_to("http://testserver%s" % destination)

    def ensure_list(self, instructions, base=''):
        """Test a list of instructions"""
        for action, args in instructions:
            if isinstance(args, basestring):
                args = (args, )

            # Add base to all args
            original_url = args[0]
            args = ["%s%s" % (base, arg) for arg in args]
            if action == 'ensure':
                # The string to check doesn't change for ensure
                args.append(original_url)

            print action, args
            getattr(self, action)(*args)

    def normal_adds(self):
        return [
              ('ensure', '/add0/')
            , ('ensure', '/add1/')
            , ('ensure', '/add1/add12/')
            , ('ensure', '/add1/add12/add123/')
            ]

    def without_target(self):
        return [
              ('refute', '/add_nt0/')
            , ('refute', '/add_nt1/')
            , ('ensure', '/add_nt1/add_nt12/')
            ]

    def promoted(self):
        return [
              ('ensure', '/ignored/one/')
            , ('ensure', '/ignored/two/')
            ]

    def with_first(self):
        return [('ensure', '/add_ntf0/')]

    def with_redirect(self):
        return [('redirects', ('/add_r0/', '/add_r0/add1'))]

def describe_maker(name, urls, base="", extra_funcs=None, extra_instructions=None):
    """Make a describe for some urls and a base"""
    funcs = {
          "works for normal adds" : 'normal_adds'
        , "doesn't give urls to those without a target" : 'without_target'
        , "gives urls to those without a section, but have a first" : 'with_first'
        , "gives urls to redirect sections" : 'with_redirect'
        , "allows urls for promoted children to appear as if not grandchildren" : 'promoted'
        }
    if extra_funcs:
        funcs.update(extra_funcs)

    def make_test_func(func_name, test_name, instructions):
        @override_settings(ROOT_URLCONF=type("urlconf", (object, ), {"urlpatterns": urls}))
        def test_func(tst):
            tst.ensure_list(getattr(tst, instructions)(), base=base)

        test_func.__name__ = func_name
        test_func.__testname__ = test_name
        return test_func

    attrs = {}
    if extra_instructions:
        attrs.update(extra_instructions)

    for test_name, instructions in funcs.items():
        func_name = "test_%s" % acceptable(test_name)
        tester = make_test_func(func_name, test_name, instructions)
        attrs[func_name] = tester

    return type(name, (SectionTesterBase, ), attrs)

########################
###   TESTS
########################

TestSection = describe_maker("TestSection", section.patterns(), base='/base')

TestAdoption = describe_maker("TestAdoption", section_foster.patterns(), base='/foster/base')

TestMerge = describe_maker("TestMerge", section_merger.patterns(), base='/merged'
    , extra_funcs = {"includes pre_merge urls" : 'pre_merge'}
    , extra_instructions = {
          'pre_merge' : lambda tst: [('ensure', '/other/')]
        }
    )
