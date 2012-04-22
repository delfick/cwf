from django.utils.translation import ugettext as _
from django.utils.functional import update_wrapper
from django.utils.encoding import force_unicode
from django.shortcuts import get_object_or_404
from django.contrib.admin.util import unquote
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.formsets import all_valid
from django.utils.text import capfirst
from django.utils.html import escape
from django.contrib import admin

import rendering

########################
###   BUTTON
########################

class ButtonMixin(object):
    def setShow(self, user, obj=None):
        condition = self.condition
        if callable(condition):
            condition = self.condition(obj, self)
        
        permissions = self.hasPermissions(user)
        if condition is False or not permissions or not self.display:
            self.show = False
        else:
            self.show = True
    
    def setProperties(self
        , kls=None, description = None
        , saveOnClick=True, forAll=False, needSuperUser=True, needsAuth=None
        , display=True, newWindow=False
        , executeAndRedirect=False
        , condition = None
        ):
        if forAll:
            saveOnClick = False
        self.kls = kls
        self.forAll = forAll
        self.display = display
        self.needsAuth = needsAuth
        self.condition = condition
        self.newWindow = newWindow
        self.saveOnClick = saveOnClick
        self.description = description
        self.needSuperUser = needSuperUser
        self.executeAndRedirect = executeAndRedirect

    def hasPermissions(self, user):
        '''Determine if user has permissions for this section'''
        if self.needSuperUser and not user.is_superuser:
            return False
        
        needsAuth = self.needsAuth
        if not needsAuth:
            return True
        
        if type(needsAuth) is bool:
            return user.is_authenticated()
        else:
            def iterAuth():
                if type(needsAuth) in (list, tuple):
                    for auth in needsAuth:
                        yield auth
                else:
                    yield needsAuth
            
            return all(user.has_perm(auth) for auth in iterAuth())

class ButtonGroup(ButtonMixin):
    def __init__(self, name, buttons, **kwargs):
        self.name = name
        self.buttons = buttons
        self.setProperties(**kwargs)
    
    @property
    def group(self):
        return True

class Button(ButtonMixin):
    def __init__(self, url, desc, **kwargs):
        self.url = url
        self.desc = desc
        self.setProperties(**kwargs)
    
    @property
    def group(self):
        return False
        
    def __unicode__(self):
        if not self.saveOnClick or self.forAll:
            link = self.link_noSaving()
        else:
            link = self.link_saving()
        return mark_safe(link)

    def link_saving(self):
        return u'<input type="submit" name="tool_%s" value="%s"/>' % (self.url, self.desc)
    
    def link_noSaving(self):
        if self.saveOnClick or not self.url.startswith('/'):
            url = "tool_%s" % self.url
        else:
            url = self.url
        
        options = []
        if self.kls:
            options.append(u'class="%s"' % self.kls)
        
        if self.newWindow:
            options.append(u'target="_blank"')
        
        return u'<a href="%s" %s>%s</a>' % (url, ' '.join(options), self.desc)

########################
###   BUTTON ADMIN MIXIN
########################

class ButtonAdminMixin(object):
    def tool_urls(self):
        """
            Mostly copied from django.contrib.admin.ModelAdmin.get_urls
            Returns patterns object for all the extra urls
        """
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name
        
        urls = []
        def iter_buttons(buttons=self.buttons):
            for button in buttons:
                if button.group:
                    for b in iter_buttons(button.buttons):
                        yield b
                else:
                    yield button
        
        for button in iter_buttons():
            urls.append(
                url(r'^(.+)/tool_%s/$' % button.url,
                    wrap(self.button_url),
                    kwargs = dict(button=button),
                    name = '%s_%s_tool_%%s' % info % button.url,
                )
            )
            
        urlpatterns = patterns('', *urls)
        return urlpatterns
    
    def button_url(self, request, object_id, button):
        """Action taken when a button is pressed"""
        model = self.model
        obj = get_object_or_404(model, pk=object_id)
        result = self.getResultForButton(request, obj, button)
    
        try:
            File, extra = result
        except:
            return result
        
        opts = model._meta
        app_label = opts.app_label
        context = {
            'title': _('%s: %s') % (button.desc, force_unicode(obj)),
            'module_name': capfirst(force_unicode(opts.verbose_name_plural)),
            'object': obj,
            'root_path': reverse('admin:index'),
            'app_label': app_label,
            'bread_title' : button.desc,
        }
        context.update(extra or {})
        return rendering.render(request, File, context)
        
    def getResultForButton(self, request, obj, button):
        name = "tool_%s" % button.url
        func = getattr(self, name, None)
        if not func and button.executeAndRedirect:
            def func(request, obj, button):
                getattr(obj, button.executeAndRedirect)()
                url = '/admin/%s/%s/%s' % (obj._meta.app_label, obj._meta.module_name, obj.id)
                return rendering.redirect(url)
            func.__name__ = name
            
        return func(request, obj, button)

########################
###   BUTTON ADMIN
########################

class ButtonAdmin(admin.ModelAdmin, ButtonAdminMixin):
    """ 
        Unfortunately I can't add these to the mixin
        , but I still want to have the mixin stuff as a mixin
    """
    
    @property
    def urls(self):
        if hasattr(self, 'buttons'):
            return self.tool_urls() + self.get_urls()
        else:
            return self.get_urls()
    
    def add_buttons(self, request, context):
        if hasattr(self, 'buttons') and self.buttons:
            [b.setShow(request.user, context.get('original')) for b in self.buttons]
            context['buttons'] = self.buttons
    
    def changelist_view(self, request, *args, **kwargs):
        """Add buttons to changelist view"""
        response = super(ButtonAdmin, self).changelist_view(request, *args, **kwargs)
        context = {}
        if hasattr(response, 'context_data'):
            context = response.context_data
        
        self.add_buttons(request, context)
        return response
    
    def render_change_form(self, request, *args, **kwargs):
        """Add buttons to change view"""
        response = super(ButtonAdmin, self).render_change_form(request, *args, **kwargs)
        context = {}
        if hasattr(response, 'context_data'):
            context = response.context_data
        
        self.add_buttons(request, context)
        return response
    
    def response_change(self, request, obj):
        redirect = None
        for key in request.POST.keys():
            if key.startswith("tool_"):
                redirect = key
        
        if redirect:
            return rendering.redirect(redirect)
        else:
            return super(ButtonAdmin, self).response_change(request, obj)
