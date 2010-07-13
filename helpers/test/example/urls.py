from django.conf.urls.defaults import *
from active import parts
site = parts.site('example')
urlpatterns = site.patterns()
