from django.conf.urls.defaults import patterns, url
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.text import capfirst
from django.contrib import admin

from cwf.views.admin_views import AdminView
from cwf.views.rendering import renderer

from functools import wraps

########################
###   BUTTON URLPATTERNS
########################

class ButtonPatterns(object):
    """
        Object to get django urlpatterns from a list of buttons
        It's based off django.contrib.admin.ModelAdmin.get_urls
    """
    def __init__(self, buttons, model, admin_view, button_view):
        self.model = model
        self.buttons = buttons
        self.admin_view = admin_view
        self.button_view = button_view

    @property
    def patterns(self):
        urls = [self.button_pattern(button) for button in self.iter_buttons()]
        return patterns('', *urls)

    def iter_buttons(self, buttons=None):
        """
            Get all buttons as a flat list
            This means using this function on nested button groups
        """
        if buttons is None:
            buttons = self.buttons

        for button in buttons:
            if button.group:
                for btn in self.iter_buttons(button.buttons):
                    yield btn
            else:
                yield button

    def button_url(self, button):
        """Get the url for this button"""
        template = r'^(.+)/tool_{}/$'
        if button.for_all:
            template = r'^tool_{}/$'
        return template.format(button.url)

    def button_name(self, button):
        """Get the view name for this button"""
        info = self.model._meta.app_label, self.model._meta.module_name
        return '%s_%s_tool_%%s' % info % button.url

    def button_func(self):
        """Wrapper to make a view for the button"""
        view = self.button_view
        def wrapper(*args, **kwargs):
            return self.admin_view(view)(*args, **kwargs)
        return update_wrapper(wrapper, view)

    def button_pattern(self, button):
        """Return pattern for this button"""
        loc = self.button_url(button)
        name = self.button_name(button)
        view = self.button_func()
        kwargs = dict(button=button)
        return url(loc, view, name=name, kwargs=kwargs)

########################
###   BUTTON ADMIN MIXIN
########################

class ButtonAdminMixin(object):
    def button_urls(self):
        """Return extra patterns for each button"""
        return ButtonPatterns(self.buttons, self.model, self.admin_site.admin_view, self.button_view).patterns

    def button_view(self, request, object_id=None, button=None):
        """Action taken when a button is pressed"""
        obj = None
        if not button.for_all:
            obj = get_object_or_404(self.model, pk=object_id)

        result = self.button_result(request, obj, button)
        if type(result) in (tuple, list) and len(result) == 2:
            template, extra = result
        else:
            return result

        context = self.button_view_context(obj, button, extra)
        return renderer.render(request, template, context)

    def button_view_context(self, obj, button, extra):
        """Get context for a button view"""
        opts = self.model._meta
        app_label = opts.app_label

        context = {
              'title': _(button.title(obj))
            , 'object': obj
            , 'app_label': app_label
            , 'root_path': reverse('admin:index')
            , 'module_name': capfirst(force_unicode(opts.verbose_name_plural))
            , 'bread_title' : button.description
            }

        if extra:
            context.update(extra)

        return context

    def button_result(self, request, obj, button):
        """
            Get result for button by finding a function for it and executing it
            Looks for tool_<button.url> on self

            If button.return_to_form then it will wrap this function and ensure that
            the user get's redirected to the form they came from.
        """
        name = "tool_{}".format(button.url)
        if not hasattr(self, name):
            raise Exception("Admin ({}) doesn't have a function for {}".format(self, name))
        func = getattr(self, name)

        if not button.return_to_form:
            return func(request, obj, button)
        else:
            @wraps(func)
            def wrapped(request, obj, button):
                """We want to redirect back to the form regardless of what the view does"""
                # Do the normal view
                func(request, obj, button)

                # Find where to redirect to and go there
                if button.for_all:
                    url = AdminView.change_list(self.model)
                else:
                    url = AdminView.change_view(obj)
                return renderer.redirect(request, url, no_processing=True)
            return wrapped(request, obj, button)

    def button_response_context(self, request, response):
        """Add the buttons to the response if there are any defined"""
        if hasattr(self, 'buttons') and self.buttons:
            # Ensure response has context data
            if not hasattr(response, 'context_data'):
                response.context_data = {}

            # Make copy of buttons for this request
            original = response.context_data.get('original')
            buttons = [btn.copy_for_request(request, original) for btn in self.buttons]

            # Give buttons as context
            response.context_data['buttons'] = buttons

########################
###   BUTTON ADMIN
########################

class ButtonAdmin(admin.ModelAdmin, ButtonAdminMixin):
    """
        Unfortunately I can't add these to the mixin
        Due to how python inheritance works
        but I still want to have the mixin stuff as a mixin
    """
    @property
    def urls(self):
        """
            Get urls for this admin
            Combine with button urls if any buttons defined on the admin
        """
        if hasattr(self, 'buttons'):
            return self.button_urls() + self.get_urls()
        else:
            return self.get_urls()

    def changelist_view(self, request, *args, **kwargs):
        """Add buttons to changelist view"""
        response = super(ButtonAdmin, self).changelist_view(request, *args, **kwargs)
        self.button_response_context(request, response)
        return response

    def render_change_form(self, request, *args, **kwargs):
        """Add buttons to change view"""
        response = super(ButtonAdmin, self).render_change_form(request, *args, **kwargs)
        self.button_response_context(request, response)
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
            return renderer.redirect(request, redirect, no_processing=True)
        else:
            return super(ButtonAdmin, self).response_change(request, obj)
