from django.template import loader, Context, Template
from should_dsl import matcher

@matcher
class RenderAs(object):
    name = 'render_as'

    def __call__(self, desired):
        self._desired = desired
        return self

    def match(self, actual):
        if type(actual) in (list, tuple):
            menu, template = actual
        else:
            menu = actual
            template = 'menu/base'
        
        extra = dict(menu=menu, children_template=template)
        t = loader.get_template('%s.html' % template)
        c = Context(extra)
        self._rendered = t.render(c)           

        # Compact and compare
        self._compact_desired = self._desired.replace('\n', '').replace('\t', '').replace('    ', '')
        self._compact_rendered = self._rendered.replace('\n', '').replace('\t', '').replace('    ', '')
        return self._compact_rendered == self._compact_desired

    def message_for_failed_should(self):
        title = "expected same (desired, rendered) => "
        return '%s"\n======================>\n"%s"\n\n======================$\n"%s"' % (
            title, self._desired, self._rendered
        )

    def message_for_failed_should_not(self):
        title = 'expected different (desired, rendered) => '
        return '%s\n======================>\n"%s"\n\n======================$\n"%s"' % (
            title, self._desired, self._rendered
        )
