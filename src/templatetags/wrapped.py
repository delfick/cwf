from django import template

register = template.Library()

class Wrapper(template.Node):
    def __init__(self, nodelist, wrap_element):
        self.nodelist = nodelist
        self.wrap_element = wrap_element
        
    def render(self, context):
        output = self.nodelist.render(context)
        wrap_element = self.wrap_element
        if not output.isspace():
            return "<{0}>\n{1}\n</{0}>".format(wrap_element, output)
        return ''

@register.tag
def wrapped(parser, token):
    _, element = token.split_contents()
    nodelist = parser.parse(('endwrapped',))
    parser.delete_first_token()
    return Wrapper(nodelist, element)
