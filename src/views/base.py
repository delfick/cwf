from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.template import loader, Context, Template
from django.shortcuts import render_to_response
from django.core import urlresolvers

from menu import Menu

import urllib
import json
import re

regexes = {
    'multi_slash' : re.compile('/+')
    }

class DictObj(dict):
    """Dictionary with attribute access"""
    def __init__(self, *args, **kwargs):
        super(DictObj, self).__init__(self, *args, **kwargs)
        self.__dict__ = self

class View(object):
    """Base class for cwf views"""
    def __call__(self, request, target, *args, **kwargs):
        """
            Called by dispatch
            determines what to call, calls it, creates template and renders it.
        """
        # Get state to put onto the request
        request.state = self.get_state(request, target)

        # Clean the args and kwargs
        self.clean_view_args(args, kwargs)

        # Get the result to render
        target_result = self.get_result(request, target, args, kwargs)
        
        # Get either (template, extra) tuple from result
        # Or if result isn't a two item tupke, just return it as is
        if type(target_result) in (tuple, list) and len(target_result) == 2:
            template, extra = target_result
        else:
            return target_result
        
        # Return extra as is if template is None
        if template is None:
            return extra
        
        # Return the response
        return self.render(request, template, extra)
    
    ########################
    ###   EXECUTE A TARGET
    ########################

    def execute(self, target, request, args, kwargs):
        """Execute target with the request, args and kwargs"""
        return getattr(self, target)(request, *args, **kwargs)

    def get_result(self, request, target, args, kwargs):
        """
            Given a request and cleaned args and kwargs
            Look at the class to determine where target is
            And use it to get a result

            Raise Exception if can't find target
            raise 404 if we find a target but it returns nothing
        """
        # If class has override method, use that instead
        if hasattr(self, 'override'):
            result = self.override(request, *args, **kwargs)
        else:
            if not hasattr(self, target):
                raise Exception, "View object doesn't have a target : %s" % target
            else:
                # Get the result from target
                result = self.execute(target, request, args, kwargs)
                
                # If the result is callable, call it with request and return
                if callable(result):
                    return result(request)
        
        if result is None:
            # Something was found but it says no
            self.raise404()

        return result

    def clean_view_args(self, args, kwargs):
        """Clean args that are to be sent to the target view"""
        # Ensure there are no trailing slashes on parts taken from url
        for key, item in kwargs.items():
            if type(item) in (str, unicode):
                while item.endswith("/"):
                    kwargs[key] = item[:-1]
    
    ########################
    ###   STATE
    ########################

    def get_state(self, request, target):
        """Get a state object for this request"""
        path = self.path_from_request(request)
        base_url = self.base_url_from_request(request)
        if base_url != '':
            path.pop(0)

        menu = Menu(request, path)
        return DictObj(
              menu = menu
            , path = path
            , target = target
            , base_url = base_url
            )
    
    ########################
    ###   RESPONSE
    ########################

    def render(self, request, template, extra=None, mime="text/plain", modify=None):
        """
            Create a template, give it context and display as some mime type

            Will get context from request.state after updating with extra

            Mime defaults to 'text/plain'

            If modify is provided and is callable
            , it is used to modify the rendered template before creating the resposen
        """
        # Get context from request.state
        # Or just a dictionary if request has no state
        if hasattr(request, 'state'):
            context = request.state
        else:
            context = {}

        # Update context with extra if it was provided
        if extra is not None:
            context.update(extra)

        # Get the template and render it
        t = loader.get_template(template)
        c = RequestContext(request, context)
        render = t.render(c)

        # Modify render if we want to
        if modify and callable(modify):
            render = modify(render)

        return HttpResponse(render, mime=mime)
    
    def raise404(self):
        """Raise a Http404"""
        raise Http404

    def http(self, *args, **kwargs):
        """Shortcut to avoid having to import HttpResponse everywhere."""
        return HttpResponse(*args, **kwargs)

    def xml(self, data):
        """Shortcut to render xml."""
        return render_to_response(data, mimetype="application/xml")

    def json(self, data):
        """Shortcut to render json"""
        return HttpResponse(json.dumps(data), mimetype='application/javascript')

    def redirect(self, request, address, *args, **kwargs):
        """Return a HttpResponseRedirect object"""
        if not kwargs.get("no_processing", False):
            address = self.redirect_address(request, address, *args, **kwargs)
        return HttpResponseRedirect(address)

    def redirect_address(self, request, address, relative=True, carry_get=False, ignore_get=None):
        """Determine address to redirect to"""
        address = unicode(address)
        base_url = self.base_url_from_request(request)
        
        def join(a, b):
            """Helper to join two urls"""
            if not a or not b:
                return '%s%s' % (a, b)
            elif b[0] == '/' and a[-1] != '/':
                return '%s%s' % (a, b)
            elif b[0] != '/' and a[-1] == '/':
                return '%s%s' % (a, b)
            else:
                return '%s/%s' % (a, b)

        if address[0] == '/':
            address = join(base_url, address)

        elif relative:
            address = join(request.path, address)

        # Make sure address has no multiple slashes
        address = regexes['multi_slash'].sub('/', address)

        if carry_get:
            get_params = self.get_params_from(request, ignore_get)
            address = "%s?%s" % (address, urllib.urlencode(get_params))

        return address

    def get_params_from(self, request, ignoreable):
        """
            Return dictionary of key value for GET params from request
            If not any ignoreable keys then just return request.GET
            Otherwise return dict with everything in request.GET except things in ignoreable
        """
        if not ignorable:
            return request.GET

        params = {}
        for key, val in request.GET.items():
            if key not in ignorable:
                params[key] = val
        return params

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
    ###   UTILITY
    ########################

    def base_url_from_request(self, request):
        """Get base url for this request"""
        if hasattr(request, 'state'):
            base_url = request.state.base_url
        else:
            base_url = request.META.get('SCRIPT_NAME', '')
        return base_url

    def path_from_request(self, request):
        """Determine the path for this request"""
        path = request.path
        if path:
            path = regexes['multi_slash'].sub('/', request.path)

        path = [p.lower() for p in path.split('/')]

        if path and path[-1] != '':
            path.append('')

        if path and path[0] != '':
            path.insert('', 1)

        return path
