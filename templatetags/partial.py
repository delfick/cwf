from django.template import Library, Node, loader, resolve_variable, TemplateSyntaxError
from django.template.context import Context

register = Library()

class repeatNode(Node):
    def __init__(self, template, menu):
        self.menu     = menu
        self.template = template

    def render(self, context):
        if self.menu:
            menu = resolve_variable(self.menu, context)
        else:
            menu = context.get('menu', None)
        import pdb
        pdb.set_trace()
        t = loader.get_template('%s.html' % self.template)
        c = Context({'menu' : menu})
        return t.render(c)

@register.tag
def repeat(parser, token):
    items = token.split_contents()
    
    template = items[1]
    menu = None
    if len(items) > 2:
        menu = items[2]
        
    return repeatNode(template, menu)
