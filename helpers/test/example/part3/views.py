from cwf_new.views import View

class views(View):
    def base(self, state):
        File = 'test.html'
        extra = {'test' : 'example.part3' }
        return File, extra
