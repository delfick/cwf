from cwf_new.views import View

class views(View):
    def base(self, request):
        File = 'test.html'
        extra = {'test' : 'example.part3' }
        return File, extra
