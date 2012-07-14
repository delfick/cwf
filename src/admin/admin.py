from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext as _
from django.utils.functional import update_wrapper
from django.utils.encoding import force_unicode
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.text import capfirst
from django.contrib import admin

from src.views.rendering import renderer

########################
###   BUTTON ADMIN MIXIN
########################

class ButtonAdminMixin(object):
    def tool_urls(self):
        """
            Mostly copied from django.contrib.admin.ModelAdmin.get_urls
            Returns patterns object for all the extra urls
        """
        urls = []
        info = self.model._meta.app_label, self.model._meta.module_name

        def iter_buttons(buttons=self.buttons):
            """
                Get all buttons as a flat list
                This means using this function on nested button groups
            """
            for button in buttons:
                if button.group:
                    for btn in iter_buttons(button.buttons):
                        yield btn
                else:
                    yield button

        def wrap(view):
            """Wrapper to make a view for the button"""
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        
        # Populate the urls
        for button in iter_buttons():
            loc = r'^(.+)/tool_%s/$' % button.url
            view = wrap(self.button_view)
            name = '%s_%s_tool_%%s' % info % button.url
            kwargs = dict(button=button)
            urls.append(url(loc, view, name=name, kwargs=kwargs))
        
        # Return the urlpatterns
        return patterns('', *urls)
    
    def button_view(self, request, object_id, button):
        """Action taken when a button is pressed"""
        model = self.model
        obj = get_object_or_404(model, pk=object_id)
        result = self.result_for_button(request, obj, button)
    
        try:
            template, extra = result
        except:
            return result
        
        opts = model._meta
        app_label = opts.app_label
        context = {
              'title': _('%s: %s') % (button.description, force_unicode(obj))
            , 'object': obj
            , 'app_label': app_label
            , 'root_path': reverse('admin:index')
            , 'module_name': capfirst(force_unicode(opts.verbose_name_plural))
            , 'bread_title' : button.description
            }

        context.update(extra or {})
        return renderer.render(request, template, context)
        
    def result_for_button(self, request, obj, button):
        """
            Get result for button by fiding a function for it and executing it
            Looks for tool_<button.url> on self
            If it can't find that and button.execute_and_redirect is True then one is made
        """
        name = "tool_%s" % button.url
        func = getattr(self, name, None)
        if not func and button.execute_and_redirect:
            def func(request, obj, button):
                getattr(obj, button.execute_and_redirect)()
                url = '/admin/%s/%s/%s' % (obj._meta.app_label, obj._meta.module_name, obj.id)
                return renderer.redirect(url, no_processing=True)
            func.__name__ = name
        
        return func(request, obj, button)

########################
###   BUTTON ADMIN
########################

class ButtonAdmin(admin.ModelAdmin, ButtonAdminMixin):
    """ 
        Unfortunately I can't add these to the mixin
        but I still want to have the mixin stuff as a mixin
    """
    @property
    def urls(self):
        """
            Get urls for this admin
            Combine with button urls if any buttons defined on the admin
        """
        if hasattr(self, 'buttons'):
            return self.tool_urls() + self.get_urls()
        else:
            return self.get_urls()
    
    def add_buttons(self, request, response):
        """Add the buttons to the response if there are any defined"""
        if hasattr(self, 'buttons') and self.buttons:
            # We have buttons. Now get context
            if hasattr(response, 'context_data'):
                context = response.context_data
            else:
                context = response.context_data = {}

            # Make copies of the buttons for this request on put on the context
            buttons = [btn.copy_for_request(request, context.get('original')) for btn in self.buttons]
            context['buttons'] = buttons
    
    def changelist_view(self, request, *args, **kwargs):
        """Add buttons to changelist view"""
        response = super(ButtonAdmin, self).changelist_view(request, *args, **kwargs)
        self.add_buttons(request, response)
        return response
    
    def render_change_form(self, request, *args, **kwargs):
        """Add buttons to change view"""
        response = super(ButtonAdmin, self).render_change_form(request, *args, **kwargs)
        self.add_buttons(request, response)
        return response
    
    def response_change(self, request, obj):
        """
            Change response to a change
            Redirects to a button if it has been set as a POST item
        """
        redirect = None
        for key in request.POST.keys():
            if key.startswith("tool_"):
                redirect = key
        
        if redirect:
            return renderer.redirect(redirect, no_processing=True)
        else:
            return super(ButtonAdmin, self).response_change(request, obj)
