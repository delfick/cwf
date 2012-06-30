# coding: spec

from src.sections.section import Section
from django.conf.urls import patterns
from django.http import HttpResponse

# The section that we're using for tests
section = Section('base')

# Function to make a view that returns response
def make_view(response):
    def view(request):
        return HttpResponse(response)
    return view

########################
###   URLS FOR TESTING
########################

# Add with no children
add0 = section.add('add0').configure(target=make_view('/base/add0/'))

# Add with children, no first
add1 = section.add('add1').configure(target=make_view('/base/add1/'))
add12 = add1.add('add12').configure(target=make_view('/base/add1/add12/'))
add123 = add12.add('add123').configure(target=make_view('/base/add1/add12/add123/'))

# Get the urlpatterns from the section to test against
urlpatterns = section.patterns()

########################
###   TESTS
########################

describe "Using Sections":
    urls = urlpatterns

    def ensure(self, url):
        """
            Ensure that going to a url gets back content equal to the url
            This is done by defining each url to explicitly return that url
        """
        ret = self.client.get(url)
        ret.status_code |should| be(200)
        ret.content |should| equal_to(url)
    
    it "works for a normal adds":
        self.ensure('/base/add0/')
        self.ensure('/base/add1/')
        self.ensure('/base/add1/add12/')
        self.ensure('/base/add1/add12/add123/')
