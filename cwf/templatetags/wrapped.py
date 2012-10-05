from django import template

register = template.Library()

class Wrapper(template.Node):
    def __init__(self, nodelist, wrap_element, attributes):
        self.nodelist = nodelist
        self._attributes = attributes
        self.wrap_element = wrap_element

    def determine_attributes(self, context):
        if not self._attributes:
            return ''

        try:
            attributes = template.Variable(self._attributes).resolve(context)
            if attributes and not attributes.startswith(" "):
                attributes = " %s" % attributes
            return attributes
        except template.VariableDoesNotExist:
            return ''

    def render(self, context):
        output = self.nodelist.render(context)
        attributes = self.determine_attributes(context)
        wrap_element = self.wrap_element

        if not output.isspace():
            return "<{0}{1}>\n{2}\n</{0}>".format(wrap_element, attributes, output)
        return ''

@register.tag
def wrapped(parser, token):
    contents = token.split_contents()
    attributes = ""
    if len(contents) == 2:
        _, element = contents
    else:
        _, element, attributes = contents

    nodelist = parser.parse(('endwrapped',))
    parser.delete_first_token()
    return Wrapper(nodelist, element, attributes)
