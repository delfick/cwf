from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext

def render(request, File, context):
    t = loader.get_template(File)
    c = RequestContext(request, context)
    return HttpResponse(t.render(c))

def redirect(redirect):
    return HttpResponseRedirect(redirect)
