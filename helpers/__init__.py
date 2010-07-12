from parts import Parts, Part as P

"""
These objects are for making life a little nicer when it comes to splitting an app into several different categories, each residing in their own folder with their own views, urls and models.

This is useful when you want everything in a single app, but there is just too much for defining in a single file.

I would structure such an app as :
    
appRoot:
    __init__.py
    urls.py
    models.py
    admin.py
    active.py
    
    templates:
        Folder containing app-wide templates
        
    part1:
        __init__.py
        urls.py
        views.py
        models.py
        admin.py
    
    part2:
        etc
        
inside the urls, models and admin python files at the app's root, you essentially collect the respective urls, models and admin data from each part.

This way, django sees everything that you've defined seperately as a single app.

Inside active.py, you have a list of references to each part specifying which one's you want to use, which is then used by the urls, models and admin to decide which part to get stuff from.

To make life easy, it comes down to the following ::

==========================
active.py
=========

from cwf.helpers import Parts, P

parts = Parts(
        __package__, globals(), locals()
      , P('part1')
      , P('part2')
      , P('part3')
      )
      
===========================


P is an alias for the Part class. You can provide keyword arguements to the P call :
    active :: default = True :: Says whether we can use this part
    Any other keyword argument is passed into the Site.add function if you choose to create a Site object using these parts


==========================
admin.py
=========

from active import parts

parts.admin(locals())

===========================
models.py
=========

from active import parts

parts.models(locals())

===========================
urls.py
=========

from django.conf.urls.defaults import *

urlpatterns = patterns(''
    , (r'^partOne$', include('myapp.part1'))
    , (r'^part2$', include('myapp.part2', namespace='p2'))
    , (r'^p3$', include("myapp.part3'))
    )

===========================

Note, that yYou probably would have a bit more of a standardised url scheme for the parts :p

Alternatively, when it comes to creating the urls, assuming you've used Section objects in the urls of each part, you can do.

===========================
urls.py
=========

from active import parts

site = parts.site('nameOfSiteObject')
urlpatterns = site.patterns()

===========================


And then you define each part in the same way you define any other app.
However, make sure that when you define a model, you give it an app_label equal to the name of your app in it's Meta class so that django sees it as being defined in your app's models.py.

So like :

    class MyAwesomeModel(models.Model):
        
        [ .. ]
        
        class Meta:
            app_label = 'nameOfMyApp'
            
And define a __all__ list at the bottom of each models.py that holds a reference to each model you want to belong to that part of the site
"""
