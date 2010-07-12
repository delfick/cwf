# coding: spec

from django.template import loader, Context, Template
from urls.section import Site, Section, Values
from .menus import Menu

@matcher
class RenderAs(object):
    name = 'render_as'

    def __call__(self, radicand):
        self._radicand = radicand
        return self

    def match(self, actual):
        menu, name = actual
        
        extra = {'menu' : menu}
        t = loader.get_template('%s.html' % name)
        c = Context(extra)
        self._expected = t.render(c)
        self._actual = '%s menu' % name
           
        self._expected = self._expected.replace('\n', '').replace('\t', '').replace('    ', '')
        self._radicand = self._radicand.replace('\n', '').replace('\t', '').replace('    ', '')
        
        return self._expected == self._radicand

    def message_for_failed_should(self):
        return 'expected "%s"\n======================>\n"%s"\n\n======================$\n"%s"' % (
            self._actual, self._radicand, self._expected)

    def message_for_failed_should_not(self):
        return 'expected "%s"\n\tTo not translate to "%s"' % (
            self._actual, self._radicand)
            
describe 'Menu templates':
    before_each:
        self.site = Site('templateTest')
        
        self.base = self.site.makeBase(inMenu=True)
        
        self.sect1 = Section('1').base(showBase=False)
        self.site.add(self.sect1, inMenu=True)
        
        self.sect1_some = self.sect1.add('some').base(alias='blah')
        self.sect1_blah = self.sect1.add('\w+').base(
                          match = 'blah'
                        , values = Values(
                            lambda path : ['2', '1', '3']
                          , lambda path, value : ('_%s' % value, '%s_' % value)
                          , sorter = True
                          )
                        )
        
        self.sect2 = Section('2').base(alias='two', showBase=False)
        self.site.add(self.sect2, inMenu=True)
        
        self.sect2_first = self.sect2.first().base(alias='meh')
        self.sect2_1 = self.sect2.add('1')
        self.sect2_1_1 = self.sect2_1.add('2').base(exists=False)
        self.sect2_1_2 = self.sect2_1.add('3')
        self.sect2_1_2_1 = self.sect2_1_2.add('4')
        
        self.sect3 = Section('3').base(display=False, showBase=False)
        self.site.add(self.sect3, inMenu=True)
        
        self.sect3.add('test1')
            
    it 'should make a global menu':
        menu = Menu(self.site, [''], self.base)
        desired = """
        <ul>
            <li class="selected"><a href=""></a></li>
            <li><a href="/1">1</a></li>
            <li><a href="/2">two</a></li>
        </ul>
        """
        
        (menu, 'global') | should | render_as(desired)
            
    it 'should make a heirarchial menu 1':
        menu = Menu(self.site, ['1'], self.sect1)
        desired = """
        <ul>
            <li><a href="/1/some">blah</a></li>
            <li><a href="/1/1_">_1</a></li>
            <li><a href="/1/2_">_2</a></li>
            <li><a href="/1/3_">_3</a></li>
        </ul>
        """
        
        (menu, 'heirarchial') | should | render_as(desired)
            
    it 'should make a heirarchial menu 2':
        menu = Menu(self.site, ['1', '1_'], self.sect1)
        desired = """
        <ul>
            <li><a href="/1/some">blah</a></li>
            <li class="selected"><a href="/1/1_">_1</a></li>
            <li><a href="/1/2_">_2</a></li>
            <li><a href="/1/3_">_3</a></li>
        </ul>
        """
        
        (menu, 'heirarchial') | should | render_as(desired)
            
    ignore 'should make a heirarchial menu 3':
        menu = Menu(self.site, ['2'], self.sect2)
        desired = """
        <ul>
            <li class="selected"><a href="/2/">meh</a></li>
            <li>
                <a href="/2/1">1</a>
                <ul>
                    <li>
                        <a href="/2/1/3">3</a>
                        <ul>
                            <li><a href="/2/1/3/4">4</a></li>
                        </ul>
                    </li>
                <ul>
            </li>
        </ul>
        """
        
        (menu, 'heirarchial') | should | render_as(desired)
            
    it 'should make a heirarchial menu 4':
        menu = Menu(self.site, ['3'], self.sect3)
        desired = "<ul></ul>"
        
        (menu, 'heirarchial') | should | render_as(desired)
            
            
            
            
            
            
            
            
            
            
            
            
            
