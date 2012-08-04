from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext, Context

from redirect_address import RedirectAddress

import json

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
        context = self.request_context(request, extra)
        template_obj = loader.get_template(template)
        render = template_obj.render(context)

        # Modify render if we want to
        if modify and callable(modify):
            render = modify(render)

        return HttpResponse(render, mime=mime)

    def request_context(self, request, extra):
        """
            Get context from request.state or empty dictionary
            Update with extra
            Return request context
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
        return RequestContext(request, context)
    
    def raise404(self):
        """Raise a Http404"""
        raise Http404

    def http(self, *args, **kwargs):
        """Shortcut to avoid having to import HttpResponse everywhere."""
        return HttpResponse(*args, **kwargs)

    def xml(self, data):
        """Shortcut to render xml."""
        return HttpResponse(data, mimetype="application/xml")

    def json(self, data):
        """
            Shortcut to render json
            If data is a string, then assume it's already json
            Otherwise use json.dumps
        """
        if type(data) not in (str, unicode):
            data = json.dumps(data)
        return HttpResponse(data, mimetype='application/javascript')

    def redirect(self, request, address, *args, **kwargs):
        """Return a HttpResponseRedirect object"""
        if not kwargs.get('no_processing', False):
            if 'no_processing' in kwargs:
                del kwargs['no_processing']
            address = RedirectAddress(request, address, *args, **kwargs).modified
        return HttpResponseRedirect(address)

# An instance that may be used
# No state is stored on the renderer
renderer = Renderer()
