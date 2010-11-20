from sphinx.writers.html import SmartyPantsHTMLTranslator
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.domains.std import StandardDomain
from sphinx.roles import XRefRole

from docutils import nodes, transforms
import os

def setup(app):    
    app.add_builder(CWF_HTML_Builder)
    app.add_transform(SuppressBlockquotes)


class SuppressBlockquotes(transforms.Transform):
    """
    Remove the default blockquotes that encase indented list, tables, etc.
    """
    default_priority = 300

    suppress_blockquote_child_nodes = (
        nodes.bullet_list,
        nodes.enumerated_list,
        nodes.definition_list,
        nodes.literal_block,
        nodes.doctest_block,
        nodes.line_block,
        nodes.table
    )

    def apply(self):
        for node in self.document.traverse(nodes.block_quote):
            if len(node.children) == 1 and isinstance(node.children[0], self.suppress_blockquote_child_nodes):
                node.replace_self(node.children[0])

class CwfHTMLTranslator(SmartyPantsHTMLTranslator):
    """
    Django-specific reST to HTML tweaks.
    """
            
    # Don't use border=1, which docutils does by default.
    def visit_table(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    # <big>? Really?
    def visit_desc_parameterlist(self, node):
        self.body.append('(')
        self.first_param = 1

    def depart_desc_parameterlist(self, node):
        self.body.append(')')

    #
    # Don't apply smartypants to literal blocks
    #
    def visit_literal_block(self, node):
        self.no_smarty += 1
        SmartyPantsHTMLTranslator.visit_literal_block(self, node)

    def depart_literal_block(self, node):
        SmartyPantsHTMLTranslator.depart_literal_block(self, node)
        self.no_smarty -= 1

    # Give each section a unique ID -- nice for custom CSS hooks
    def visit_section(self, node):
        old_ids = node.get('ids', [])
        node['ids'] = ['s-' + i for i in old_ids]
        node['ids'].extend(old_ids)
        SmartyPantsHTMLTranslator.visit_section(self, node)
        node['ids'] = old_ids
        
class CWF_HTML_Builder(StandaloneHTMLBuilder):

    name = 'cwfhtml'
    
    def write_genindex(self):
        # the total count of lines for each index letter, used to distribute
        # the entries into two columns
        genindex = self.env.create_index(self)

        for key, entries in genindex:
            for index, (name, (links, subitems)) in enumerate(entries):
                if len(subitems) == 1 and not links:
                    entries[index] = ('%s (%s)' % (name, subitems[0][0]), [subitems[0][1], []])

        indexcounts = []
        for _, entries in genindex:
            indexcounts.append(sum(1 + len(subitems)
                                   for _, (_, subitems) in entries))
        
        genindexcontext = dict(
            genindexentries = genindex,
            genindexcounts = indexcounts,
            split_index = self.config.html_split_index,
        )
        self.info(' genindex', nonl=1)
        #import pdb
        #pdb.set_trace()
        if self.config.html_split_index:
            self.handle_page('genindex', genindexcontext,
                             'genindex-split.html')
            self.handle_page('genindex-all', genindexcontext,
                             'genindex.html')
            
            for (key, entries), count in zip(genindex, indexcounts):
                ctx = {'key': key, 'entries': entries, 'count': count,
                       'genindexentries': genindex}
                self.handle_page('genindex-' + key, ctx,
                                 'genindex-single.html')
        else:
            self.handle_page('genindex', genindexcontext, 'genindex.html')
