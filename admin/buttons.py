from django.utils.translation import ugettext as _
from django.utils.functional import update_wrapper
from django.utils.encoding import force_unicode
from django.shortcuts import get_object_or_404
from django.contrib.admin.util import unquote
from django.utils.safestring import mark_safe
from django.forms.formsets import all_valid
from django.utils.text import capfirst
from django.utils.html import escape
from django.contrib import admin

import rendering

########################
###   BUTTON
########################

class Button(object):
    def __init__(self
        , url, desc
        , kls=None, saveOnClick=True, forAll=False, display=True, needSuperUser=True):
        
        if forAll:
            saveOnClick = False
        self.url = url
        self.kls = kls
        self.desc = desc
        self.forAll = forAll
        self.display = display
        self.saveOnClick = saveOnClick
        self.needSuperUser = needSuperUser
        
    def __unicode__(self):
        if not self.saveOnClick or self.forAll:
            link = self.link_noSaving()
        else:
            link = self.link_saving()
        return mark_safe(link)
    
    def link_noSaving(self):
        if self.saveOnClick or not self.url.startswith('/'):
            url = "tool_%s" % self.url
        else:
            url = self.url
        
        kls = ""
        if self.kls:
            kls = u' class="%s"' % self.kls
        
        return u'<a href="%s" %s>%s</a>' % (url, kls, self.desc)

    def link_saving(self):
        return u'<input type="submit" name="tool_%s" value="%s"/>' % (self.url, self.desc)
    
    def setShow(self, user):
        if (self.needSuperUser and not user.is_superuser) or not self.display:
            self.show = False
        else:
            self.show = True

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
        for button in self.buttons:
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
        result = getattr(self, "tool_%s" % button.url)(request, obj, button)
        
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
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'bread_title' : button.desc,
        }
        context.update(extra or {})
        return rendering.render(request, File, context)

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
    
    def changelist_view(self, request, extra_context=None):
        """Add buttons to changelist view"""
        if not extra_context:
            extra_context = {}
        
        if hasattr(self, 'buttons') and self.buttons:
            [b.setShow(request.user) for b in self.buttons]
            extra_context['buttons'] = self.buttons
        
        return super(ButtonAdmin, self).changelist_view(request, extra_context)
        
    def change_view(self, request, object_id, extra_context=None):
        """Add buttons to change view"""
        if not extra_context:
            extra_context = {}
        
        if hasattr(self, 'buttons') and self.buttons:
            [b.setShow(request.user) for b in self.buttons]
            extra_context['buttons'] = self.buttons
        
        result = super(ButtonAdmin, self).change_view(request, object_id, extra_context)
        
        redirect = None
        for key in request.POST.keys():
            if key.startswith("tool_"):
                redirect = key
                
        if not redirect:
            return result
        else:
            # A lot of this is copied from django.contrib.admin.ModelAdmin.change_view
            model = self.model
            opts = model._meta

            try:
                obj = self.queryset(request).get(pk=unquote(object_id))
            except model.DoesNotExist:
                # Don't raise Http404 just yet, because we haven't checked
                # permissions yet. We don't want an unauthenticated user to be able
                # to determine whether a given object exists.
                obj = None

            if not self.has_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                raise Http404(
                    _('%(name)s object with primary key %(key)r does not exist.') % {
                          'name': force_unicode(opts.verbose_name)
                        , 'key': escape(object_id)
                        }
                    )

            if request.method == 'POST' and request.POST.has_key("_saveasnew"):
                return self.add_view(request, form_url='../add/')

            ModelForm = self.get_form(request, obj)
            formsets = []
            if request.method == 'POST':
                form = ModelForm(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    form_validated = True
                    new_object = self.save_form(request, form, change=True)
                else:
                    form_validated = False
                    new_object = obj
                prefixes = {}
                for FormSet, inline in zip(
                    self.get_formsets(request, new_object), self.inline_instances):
                    prefix = FormSet.get_default_prefix()
                    prefixes[prefix] = prefixes.get(prefix, 0) + 1
                    if prefixes[prefix] != 1:
                        prefix = "%s-%s" % (prefix, prefixes[prefix])
                    
                    formset = FormSet(
                          request.POST, request.FILES, instance=new_object, prefix=prefix
                        , queryset=inline.queryset(request)
                        )
                    
                    formsets.append(formset)
                
                if all_valid(formsets) and form_validated:
                    self.save_model(request, new_object, form, change=True)
                    form.save_m2m()
                    for formset in formsets:
                        self.save_formset(request, form, formset, change=True)
                    
                    change_message = self.construct_change_message(request, form, formsets)
                    self.log_change(request, new_object, change_message)
                    
                    # Redirect instead of return normal response
                    return rendering.redirect(redirect)
        
        # Wasn't a POST or errors when saved
        return result
