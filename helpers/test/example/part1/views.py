from cwf_new.views import View

class views(View):
    def base(self, state):
        File = 'test.html'
        extra = {'test' : 'example.part1.base' }
        return File, extra
    
    def test(self, state, sect, other=False):
        File = 'test.html'
        extra = {'test' : sect }
        if other:
            extra['test'] += ' :D'
        return File, extra
