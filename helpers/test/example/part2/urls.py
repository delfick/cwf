from cwf_new.urls import init

section = init(__package__)

section.add("apart").base(target='apart')

urlpatterns = section.patterns()
