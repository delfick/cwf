from cwf_new.views import View

class views(View):
    def base(self, state):
        File = 'test.html'
        extra = {'test' : 'example.part2.base' }
        return File, extra

    def apart(self, state):
        File = 'test.html'
        extra = {'test' : 'example.part2.apart' }
        return File, extra
