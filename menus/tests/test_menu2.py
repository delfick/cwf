# coding: spec

from django.template import loader, Context, Template
from urls.section import Site, Section, Values
from menus import Menu

@matcher
class RenderAs(object):
    name = 'render_as'

    def __call__(self, radicand):
        self._radicand = radicand
        return self

    def match(self, actual):
        if len(actual) == 3:
            menu, name, gen = actual
        else:
            menu, name = actual
            gen = name
        
        extra = {'gen' : getattr(menu, gen)()}
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
        
        self.base = self.site.makeBase(inMenu=True).base(alias="Home")
        
        self.sect1 = Section('one').base(showBase=False)
        self.site.add(self.sect1, inMenu=True)
        
        self.sect1_some = self.sect1.add('some').base(alias='blah')
        self.sect1_blah = self.sect1.add('\w+').base(
                          match = 'blah'
                        , values = Values(
                            lambda (r, pu, p) : ['2', '1', '3']
                          , lambda (r, pu, p), value : ('_%s' % value, '%s_' % value)
                          , sorter = True
                          )
                        )
        
        self.sect2 = Section('2').base(alias='two', showBase=False)
        self.site.add(self.sect2, inMenu=True)
        
        self.sect2_first = self.sect2.first().base(alias='meh')
        self.sect2_1 = self.sect2.add('1')
        self.sect2_1_1 = self.sect2_1.add('2').base(active=False)
        self.sect2_1_2 = self.sect2_1.add('3')
        self.sect2_1_2_1 = self.sect2_1_2.add('4')
        
        self.sect3 = Section('3').base(display=False, showBase=False)
        self.site.add(self.sect3, inMenu=True)
        
        self.sect3.add('test1')
        
        self.sect4 = Section('4').base(showBase=False)
        self.sect4_1 = self.sect4.add('this')
        self.sect4_2 = self.sect4.add('needs')
        self.sect4_4 = self.sect4.add('more')
        self.sect4_5 = self.sect4.add('creativity')
        
        self.sect4_2_1 = self.sect4_2.add('a')
        self.sect4_2_2 = self.sect4_2.add('path')
        self.sect4_2_3 = self.sect4_2.add('going')
        self.sect4_2_4 = self.sect4_2.add('somewhere')
        
        self.sect4_2_2_1 = self.sect4_2_2.add('\w+').base(
                           values = Values(['1', '2', '3'], asSet=False)
                         )
        
        self.sect4_2_2_1_1 = self.sect4_2_2_1.add('meh')
                         
        self.sect4_4_1 = self.sect4_4.add('test')
        self.sect4_4_2 = self.sect4_4.add('blah')
            
    it 'should make a global menu with base selected':
        menu = Menu(self.site, [], self.base)
        desired = """
        <ul>
            <li class="selected"><a href="/">Home</a></li>
            <li><a href="/one">One</a></li>
            <li><a href="/2">two</a></li>
        </ul>
        """
        
        (menu, 'base', 'getGlobal') | should | render_as(desired)
    
    it 'should make a global menu with section other than base selected':
        menu = Menu(self.site, ['one'], self.base)
        desired = """
        <ul>
            <li><a href="/">Home</a></li>
            <li class="selected"><a href="/one">One</a></li>
            <li><a href="/2">two</a></li>
        </ul>
        """
        
        (menu, 'base', 'getGlobal') | should | render_as(desired)
    
    it 'should make global menu and be case insensitive':
        menu = Menu(self.site, ['oNe'], self.base)
        desired = """
        <ul>
            <li><a href="/">Home</a></li>
            <li class="selected"><a href="/one">One</a></li>
            <li><a href="/2">two</a></li>
        </ul>
        """
        
        (menu, 'base', 'getGlobal') | should | render_as(desired)
    
    it 'should make global menu when the url is longer than selected section':
        menu = Menu(self.site, ['one', 'some'], self.base)
        desired = """
        <ul>
            <li><a href="/">Home</a></li>
            <li class="selected"><a href="/one">One</a></li>
            <li><a href="/2">two</a></li>
        </ul>
        """
        
        (menu, 'base', 'getGlobal') | should | render_as(desired)
        
    describe 'heirarchial menu':
        it 'should make a heirarchial menu':
            menu = Menu(self.site, ['one'], self.sect1)
            desired = """
            <ul>
                <li><a href="/one/some">blah</a></li>
                <li><a href="/one/1_">_1</a></li>
                <li><a href="/one/2_">_2</a></li>
                <li><a href="/one/3_">_3</a></li>
            </ul>
            """
            
            (menu, 'heirarchial') | should | render_as(desired)
            
        it 'should make a heirarchial menu when ending in a number':
            site = Site('main')
            meh = Section('')
            site.add(meh, inMenu=True, includeAs='blah')
            
            meh.first().base(alias='latest')
            
            b = meh.add('meh')
            b2 = b.add('\d{4}').base(match='year', values=Values([2010, 2009], asSet=False))
            h = b2.add('\d+').base(match='asdf', values=Values([1], asSet=False))
            
            menu = Menu(site, ['blah', 'meh', '2010', '1'], h.rootAncestor())
            desired = """
            <ul>
                <li><a href="/blah">latest</a></li>
                <li class="selected">
                    <a href="/blah/meh">Meh</a>
                    <ul>
                        <li class="selected">
                            <a href="/blah/meh/2010">2010</a>
                            <ul>
                                <li class="selected">
                                    <a href="/blah/meh/2010/1">1</a>
                                </li>
                            </ul>
                        </li>
                        <li><a href="/blah/meh/2009">2009</a></li>
                    </ul>
                </li>
            </ul>
            """
            
            (menu, 'heirarchial') | should | render_as(desired)
                
        it 'should support sections with multiple values':
            menu = Menu(self.site, ['one', '1_'], self.sect1)
            desired = """
            <ul>
                <li><a href="/one/some">blah</a></li>
                <li class="selected"><a href="/one/1_">_1</a></li>
                <li><a href="/one/2_">_2</a></li>
                <li><a href="/one/3_">_3</a></li>
            </ul>
            """
            
            (menu, 'heirarchial') | should | render_as(desired)
                
        it 'should make a heirarchial menu and not include children when parent isnt selected':
            menu = Menu(self.site, ['2'], self.sect2)
            desired = """
            <ul>
                <li class="selected"><a href="/2">meh</a></li>
                <li><a href="/2/1">1</a></li>
            </ul>
            """
            
            (menu, 'heirarchial') | should | render_as(desired)
                
        it 'should make a heirarchial menu and do include children when parent is selected':
            menu = Menu(self.site, ['2', '1', '3', '4'], self.sect2)
            desired = """
            <ul>
                <li><a href="/2">meh</a></li>
                <li class="selected">
                    <a href="/2/1">1</a>
                    <ul>
                        <li class="selected">
                            <a href="/2/1/3">3</a>
                            <ul>
                                <li class="selected"><a href="/2/1/3/4">4</a></li>
                            </ul>
                        </li>
                    </ul>
                </li>
            </ul>
            """
            
            (menu, 'heirarchial') | should | render_as(desired)
                
        it 'should not show sections that have display set to False':
            menu = Menu(self.site, ['3'], self.sect3)
            desired = ""
            
            (menu, 'heirarchial') | should | render_as(desired)
    
    describe 'layered menu':
        it 'should be able to handle no selected section':
            menu = Menu(self.site, ['one'], self.sect1)
            desired = """
            <ul>
                <li><a href="/one/some">blah</a></li>
                <li><a href="/one/1_">_1</a></li>
                <li><a href="/one/2_">_2</a></li>
                <li><a href="/one/3_">_3</a></li>
            </ul>
            """
            
            (menu, 'layered') | should | render_as(desired)
        
        it 'should only create layers from children with selected parents':
            menu = Menu(self.site, ['2'], self.sect2)
            desired = """
            <ul>
                <li class="selected"><a href="/2">meh</a></li>
                <li><a href="/2/1">1</a></li>
            </ul>
            """
            
            (menu, 'layered') | should | render_as(desired)
                
        it 'should be able to make a layered menu':
            menu = Menu(self.site, ['4', 'needs', 'path', '2'], self.sect4)
            desired = """
            <ul>
                <li><a href="/4/this">This</a></li>
                <li class="selected"><a href="/4/needs">Needs</a></li>
                <li><a href="/4/more">More</a></li>
                <li><a href="/4/creativity">Creativity</a></li>
            </ul>
            <ul>
                <li><a href="/4/needs/a">A</a></li>
                <li class="selected"><a href="/4/needs/path">Path</a></li>
                <li><a href="/4/needs/going">Going</a></li>
                <li><a href="/4/needs/somewhere">Somewhere</a></li>
            </ul>
            <ul>
                <li><a href="/4/needs/path/1">1</a></li>
                <li class="selected"><a href="/4/needs/path/2">2</a></li>
                <li><a href="/4/needs/path/3">3</a></li>
            </ul>
            <ul>
                <li><a href="/4/needs/path/2/meh">Meh</a></li>
            </ul>
            """
            
            (menu, 'layered') | should | render_as(desired)
            
        it 'should not show sections that have display set to False':
            menu = Menu(self.site, ['3'], self.sect3)
            desired = ""
            
            (menu, 'layered') | should | render_as(desired)
            
            
            
            
            
            
            
            
            
            
