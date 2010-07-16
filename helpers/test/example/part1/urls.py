from cwf.urls import init, V

section = init(__package__)

section.first()

test = section.add('\w+').base(''
     , match  = 'sect'
     , target = 'test'
     , values = V(['some', 'nice', 'place'])
     )
     
test.add('meh').base(''
    , extraContext = {'other' : True}
)

urlpatterns = section.patterns()
