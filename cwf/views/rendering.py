from django.template.backends.django import Template as BackendTemplate
from django.template import loader, RequestContext, Context, Template
from django.http import HttpResponse, Http404, HttpResponseRedirect

from redirect_address import RedirectAddress

import json

class Renderer(object):
    """
        Stateless class that simplifies usage of Django machinary for creating HttpResponse objects

        An instantiated instance of this class is provided from ``cwf.views.rendering.renderer``
    """
    def simple_render(self, template, extra):
        """Return the string from rendering specified template with a normal Context object"""
        t = loader.get_template(template)
        c = Context(extra)
        return t.render(c)

    def render(self, request, template, extra=None, mime="text/html", modify=None):
        """
            Create a template, give it context and display as some mime type

            Using a RequestContext object provided by ``self.request_context``

            If modify is provided and is callable then it will be used
            to modify the rendered template before creating the HttpResponse object
        """
        context = self.request_context(request, extra)
        if isinstance(template, Template) or isinstance(template, BackendTemplate):
            template_obj = template
        else:
            template_obj = loader.get_template(template)
        render = template_obj.render(context)

        # Modify render if we want to
        if modify and callable(modify):
            render = modify(render)

        return HttpResponse(render, content_type=mime)

    def request_context(self, request, extra):
        """
            Create a RequestContext object from the request and extra context provided.

            If request has a ``state`` member, that will be used as default context
            , otherwise an empty dictionary is used, which is updated with the ``extra`` context provided.
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
        """Return a HttpResponse object with the args and kwargs passed in"""
        return HttpResponse(*args, **kwargs)

    def xml(self, data):
        """Return HttpResponse object with data and a 'application/xml' content_type"""
        return HttpResponse(data, content_type="application/xml")

    def json(self, data):
        """Return HttpResponse object with data dumped as a json string and a 'application/javascript' content_type"""
        if type(data) not in (str, unicode):
            data = json.dumps(data)
        return HttpResponse(data, content_type='application/javascript')

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
