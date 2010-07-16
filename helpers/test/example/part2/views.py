from cwf.views import View

class views(View):
    def base(self, request):
        File = 'test.html'
        extra = {'test' : 'example.part2.base' }
        return File, extra

    def apart(self, request):
        File = 'test.html'
        extra = {'test' : 'example.part2.apart' }
        return File, extra
