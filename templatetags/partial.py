from django.template import Library, Node, loader, resolve_variable, TemplateSyntaxError
from django.template.context import Context

register = Library()

class repeatNode(Node):
    def __init__(self, gen, template):
        self.gen      = gen
        self.template = template

    def render(self, context):
        if self.gen:
            gen = resolve_variable(self.gen, context)
        else:
            gen = context.get('gen', None)
        
        if callable(gen):
            gen = gen()
        
        t = loader.get_template(self.template.replace('"', '').replace("'", ''))
        c = Context({'gen' : gen})
        return t.render(c)

@register.tag
def repeat(parser, token):
    items = token.split_contents()
    
    menu = None
    if len(items) > 2:
        menu = items[1]
        template = items[2]
        
    return repeatNode(menu, template)
