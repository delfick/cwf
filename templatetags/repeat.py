from django.template import Library, Node, loader, resolve_variable, TemplateSyntaxError
from django.template import Variable, VariableDoesNotExist
from django.template.context import Context

register = Library()

class repeatNode(Node):
    def __init__(self, gen, template):
        self.gen      = Variable(gen)
        self.template = template

    def render(self, context):
        gen = context.get('gen', None)
        if self.gen:
            try:
                gen = self.gen.resolve(context)
            except VariableDoesNotExist:
                pass

        if gen:
            if callable(gen):
                gen = gen()
            
            t = loader.get_template(self.template.replace('"', '').replace("'", ''))
            context['gen'] = gen
            c = Context(context)
            return t.render(c)
        
        return ''

@register.tag
def repeat(parser, token):
    items = token.split_contents()
    
    menu = None
    if len(items) > 2:
        menu = items[1]
        template = items[2]
        
    return repeatNode(menu, template)

class WithWrapNode(Node):
    def __init__(self, nodelist, wrapWith):
        self.nodelist = nodelist
        self.wrapWith = wrapWith
        
    def render(self, context):
        output = self.nodelist.render(context)
        if not output.isspace():
            return "<%s>\n%s\n</%s>" % (self.wrapWith, output, self.wrapWith)
        
        return ''

@register.tag
def withul(parser, token):
    nodelist = parser.parse(('endwithul',))
    parser.delete_first_token()
    return WithWrapNode(nodelist, 'ul')

@register.tag
def withli(parser, token):
    nodelist = parser.parse(('endwithli',))
    parser.delete_first_token()
    return WithWrapNode(nodelist, 'li')
