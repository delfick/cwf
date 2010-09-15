from django.contrib.admin.views.decorators import staff_member_required
from django.template import loader, RequestContext, Context, Template
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.core import urlresolvers
from django.utils import simplejson
from django.conf import settings
from datetime import datetime

from cwf.menus import Menu

import re

defaultSite = None
if hasattr(settings, 'SITE'):
    try:
        defaultSite = __import__(settings.SITE, globals(), locals(), ['site'], -1).site
    except ImportError:
        pass

if hasattr(settings, 'PROJECTDIR'):
    projectDir = settings.PROJECTDIR
else:
    projectDir = '/var/www'
    
regexes = {
    'multiSlash' : re.compile('/+'),
}

########################
###  
###   CONVENIENCE OBJECT
###  
########################    

class DictObj(object):
    def __init__(self, **kwargs):
        self.theKeys = {}
        self.update(kwargs)
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def __setattr__(self, key, value):
        if key not in ['self', 'theKeys']:
            self.theKeys[key] = True
        
        object.__setattr__(self, key, value)
    
    def __iter__(self):
        for key in self.theKeys.keys():
            yield key
    
    def keys(self):
        return self.theKeys.keys()
    
    def values(self):
        return [self[key] for key in self.theKeys.keys()]
    
    def items(self):
        return [(key, self[key]) for key in self.theKeys.keys()]
    
    def update(self, values):
        for key, value in values.items():
            self[key] = value
    
########################
###  
###   BASE VIEW KLS
###  
########################    

class View(object):
    """Base view class for cwf"""
    
    def __init__(self):
        self.projectDir = projectDir
    
    def getState(self, request, target, site, section):
        """This is to be passed around everywhere and represents state for one request.
        This is to avoid storing state on the class itself which is only ever instantiated once"""
        if not site:
            site = defaultSite
            
        state = DictObj( baseUrl = request.META.get('SCRIPT_NAME', '')
                       , section = section
                       , target  = target
                       , site    = site
                       )
            
        path = request.path
        if path.startswith('/'):
            path = path[1:]
        
        if path:
            path = regexes['multiSlash'].sub('/', request.path)
            
        path = [p.lower() for p in path.split('/')]
        
        if path[0] == '':
            path.pop(0)
        
        if state.baseUrl != "":
            path.pop(0)
        
        if section:
            state.menu = Menu(site, path, section.rootAncestor(), request=request)
        
        return state
    
    ########################
    ###   CALL STUFF
    ########################

    def updateState(self, request, state, extra=None):
        """Used by the View to insert any extra variables for use in the template."""
        
        if state is None:
            state = DictObj()
        
        if extra:
            state.update(extra)
        
        return state
    
    def getResult(self, request, target, *args, **kwargs):
        """Used to determine what function to call, and actually call it."""
        return getattr(self, target)(request, *args, **kwargs)
    
    def __call__(self, request, target, section, site=None, *args, **kwargs):
        """Called by dispatch and determines what to call, calls it, creates template and renders it."""
        state = self.getState(request, target, site, section)
        request.state = state
        
        # Ensure there are no trailing slashes on parts taken from url
        for key, item in kwargs.items():
            if type(item) in (str, unicode):
                if item[-1] == '/':
                    kwargs[key] = item[:-1]
        
        result = None
        # If class has override method, use that instead
        if hasattr(self, 'override'):
            result = self.override(request, *args, **kwargs)
        
        # If there was no override ::
        if not result:
            if hasattr(self, target):
                # Get the result from target
                result = self.getResult(request, target, *args, **kwargs)
                
                # If it's callable, give it state and return result
                if callable(result):
                    return result(request)
                
            else:
                raise Exception, "View object doesn't have a target : %s" % target
        
        # Was no result, view doesn't exist
        if not result:
            self.raise404()
        
        # Get either File, extra tuple from result or just return
        if type(result) in (tuple, list) and len(result) == 2:
            File, extra = result
        else:
            return result
        
        # If File is None, assume extra is a HttpResponse
        if File is None:
            return extra
        
        # Add extra varaibles to state object
        state = self.updateState(request, request.state, extra)
        
        # Create the template
        t = loader.get_template(File)
        c = RequestContext(request, state)
        
        try:
            render = t.render(c)
        except Exception, error:
            import traceback
            raise Exception, (error, traceback.format_exc())
        
        # Render !
        return HttpResponse(render)
    
    ########################
    ###   RAISES/RETURNS
    ########################    
    
    def raise404(self):
        raise Http404

    def http(self, *args, **kwargs):
        """Shortcut to avoid having to import HttpResponse everywhere."""
        return HttpResponse(*args, **kwargs)

    def xml(self, address):
        """Shortcut to render xml."""
        return render_to_response(address, mimetype="application/xml")
    
    def _redirect(self, request, address, relative=True, carryGET=False, ignoreGET=None):
        """Get's address used by redirect"""
        address = unicode(address)
        
        if hasattr(request, 'state'):
            baseUrl = request.state.baseUrl
        else:
            baseUrl = request.META.get('SCRIPT_NAME', '')
            
        if address[0] == '/':
            address = '%s%s' % (baseUrl, address)
        
        elif relative:
            address = "%s/%s" % (request.path, address)
        
        if carryGET:
            address = "%s?%s" % (address, self.getGETString(request, ignoreGET))
        
        return address.replace('//', '/')
            
    def redirect(self, request, *args, **kwargs):
        """Return a HttpResponseRedirect object"""
        address = self._redirect(request, *args, **kwargs)            
        return HttpResponseRedirect(address)
    
    def render(self, request, File, extra, mime="text/plain", modify=None):
        """Shortcut to create a template, give it context and display as some mime type (default to plain text)"""
        request.state.update(extra)
        t = loader.get_template(File)
        c = RequestContext(request, request.state)
        
        try:
            render = t.render(c)
        except Exception, error:
            import traceback
            raise Exception, (error, traceback.format_exc())
        
        if modify and callable(modify):
            render = modify(render)
            
        return HttpResponse(render, mime) 
        
    ########################
    ###   UTILITY
    ########################
    
    def getGETString(self, request, ignoreGET=None):
        """Returns GET string using request"""
        if ignoreGET is None:
            ignoreGET = []
        
        if type(ignoreGET) in (str, unicode):
            ignoreGET = [ignoreGET]
            
        options = []
        for key, value in request.GET.items():
            if key not in ignoreGET:
                if value:
                    options.append('%s=%s' % (key, value))
                else:
                    options.append('%s' % key)
                    
        return ';'.join(options)
        
    ########################
    ###   ADMIN
    ########################
    
    def getAdminChangeView(self, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(obj.id,))
        
    def getAdminAddView(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return urlresolvers.reverse("admin:%s_%s_add" % (content_type.app_label, content_type.model))
    
    def getAdminChangeList(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return urlresolvers.reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model))
    
########################
### 
###   STAFF VIEW
### 
######################## 

class StaffView(View):
    def getResult(self, request, target, *args, **kwargs):
        def view(request, *args, **kwargs):
            return getattr(self, target)(request, *args, **kwargs)
        
        return staff_member_required(view)(request, *args, **kwargs)

########################
### 
###   LOCAL ONLY
### 
######################## 

class LocalOnlyView(View):
    def getResult(self, request, target, *args, **kwargs):  
        ip = request.META.get('REMOTE_ADDR')
        if ip == '127.0.0.1':
            return getattr(self, target)(request, *args, **kwargs)
        else:
            self.raise404()
            
########################
### 
###   JAVASCRIPT
### 
######################## 

class JSView(View):
    def getResult(self, request, target, *args, **kwargs):  
        result = super(JSView, self).getResult(request, target, *args, **kwargs)
        File, extra = result
        return HttpResponse(simplejson.dumps(extra), mimetype='application/javascript')

