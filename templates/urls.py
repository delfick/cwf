from django.conf.urls import patterns, url
from django.http import HttpResponse

def index(request):
    return HttpResponse("hi")

urlpatterns = patterns('', url(r'.+', index))
