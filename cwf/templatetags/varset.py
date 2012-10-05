from django.utils.safestring import SafeString
from django import template

register = template.Library()

class VarSetter(template.Node):
    def __init__(self, nodelist, varname):
        self.varname = varname
        self.nodelist = nodelist

    def render(self, context):
        variable = self.nodelist.render(context).strip()
        context[self.varname] = SafeString(variable)
        return ''

@register.tag
def varset(parser, token):
    _, varname = token.split_contents()
    nodelist = parser.parse(('endvarset',))
    parser.delete_first_token()
    return VarSetter(nodelist, varname)
