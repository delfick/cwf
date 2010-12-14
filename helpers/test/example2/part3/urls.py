from cwf.urls import init

section = init(__package__)
section.first()

urlpatterns = section.patterns()
