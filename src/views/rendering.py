from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext, Context
from django.shortcuts import render_to_response
from django.utils.http import urlencode

class Renderer(object):
    """Class that holds django logic for rendering things"""
    def simple_render(self, template, extra):
        """Very simple render with no request context"""
        t = loader.get_template(template)
        c = Context(extra)
        return t.render(c)

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
            address = "%s?%s" % (address, urlencode(get_params))

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

# An instance that may be used
# No state is stored on the renderer
renderer = Renderer()
