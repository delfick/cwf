from base import View

class StaffView(View):
    def execute(self, target, request, args, kwargs):
        def view(request, *args, **kwargs):
            return super(StaffView, self).execute(target, request, args, kwargs)
        return staff_member_required(view)(request, *args, **kwargs)

class LocalOnlyView(View):
    def execute(self, target, request, args, kwargs):  
        ip = request.META.get('REMOTE_ADDR')
        if ip != '127.0.0.1':
            self.raise404()
        return super(LocalOnlyView, self).execute(target, request, args, kwargs)

class JSView(View):
    def execute(self, target, request, args, kwargs):  
        result = super(JSView, self).execute(target, request, *args, **kwargs)
        template, data = result
        return self.json(data)
