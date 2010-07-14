from cwf_new.views import View

class views(View):
    def base(self, request):
        File = 'test.html'
        extra = {'test' : 'example.part1.base' }
        return File, extra
    
    def test(self, request, sect, other=False):
        File = 'test.html'
        extra = {'test' : sect }
        if other:
            extra['test'] += ' :D'
        return File, extra
