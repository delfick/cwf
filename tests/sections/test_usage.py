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

# Add with no target and no children
add_nt0 = section.add('add_nt0')

# Add with no target and children
add_nt1 = section.add('add_nt1')
add_nt12 = add_nt1.add('add_nt12').configure(target=make_view('/base/add_nt1/add_nt12/'))

# Add with no target and no children but a first
add_ntf0 = section.add('add_ntf0')
add_ntf0.first().configure(target=make_view('/base/add_ntf0/'))

# Add with a redirect
add_r0 = section.add('add_r0').configure(redirect="/add1")

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
        ret.status_code |should| equal_to(200)
        ret.content |should| equal_to(url)

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
        ret = self.client.get(url)
        ret.status_code |should| equal_to(301)
        dict(ret.items())['Location'] |should| equal_to("http://testserver%s" % destination)
    
    it "works for a normal adds":
        self.ensure('/base/add0/')
        self.ensure('/base/add1/')
        self.ensure('/base/add1/add12/')
        self.ensure('/base/add1/add12/add123/')

    it "doesn't give urls to those without a target":
        self.refute('/base/add_nt0/')
        self.refute('/base/add_nt1/')
        self.ensure('/base/add_nt1/add_nt12/')

    it "gives urls to those without a section, but have a first":
        self.ensure('/base/add_ntf0/')

    it "gives urls to redirect sections":
        self.redirects('/base/add_r0/', '/add1')
