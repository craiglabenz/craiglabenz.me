# Django
from django import template

register = template.Library()


@register.tag('render_with_snippets')
def do_render_with_snippets(parser, token):
    '''
    Call this like so:

        {% render_with_snippets entry %}
    '''
    tag_name, obj_and_attr = token.split_contents()
    obj, attr = obj_and_attr.split('.')
    return SnippetNode(obj, attr)


class SnippetNode(template.Node):

    code_delimiter = "|||"
    code_delimiter_len = len(code_delimiter)

    vulnerable_languages = ["markup", "xml"]

    def __init__(self, obj, attr):
        '''
        Arguments
        obj     {str}   The name of the attr in this context
        attr    {str}   The attr on `obj` we want to render
        '''
        self.obj = obj
        self.attr = attr

    def render(self, context):
        '''
        Finds -s-snippet-slug- style chunks in the `obj`'s `attr` attribute
        and replaces them with the corresponding snippet's highlighted html.
        '''
        # Pull our object out of the context
        obj = context[self.obj]

        # Extract the corresponding attribute (likely something like `body_html`)
        attr = getattr(obj, self.attr)

        while "|||" in attr:
            attr, most_recent_snippet = self.parse_code_block(attr)

            if not attr.endswith(most_recent_snippet):
                fancier_snippet = most_recent_snippet + """\n<div class="entry-body-wrapper">"""
                attr = attr.replace(most_recent_snippet, fancier_snippet)

        # Once the loop breaks, we're good
        return attr

    def parse_code_block(self, attr):
        start_pos = attr.find(self.code_delimiter)
        next_newline_pos = attr[self.code_delimiter_len + start_pos:].find("\n") + start_pos + self.code_delimiter_len

        # Snippet language
        snippet_language = attr[start_pos + self.code_delimiter_len:next_newline_pos]

        # Capture all the code
        snippet_end = attr[next_newline_pos:].find("|||") + next_newline_pos
        code = attr[next_newline_pos:snippet_end]

        # Handle language-specific prism gotchas
        if snippet_language in self.vulnerable_languages:
            code = code.replace("<", "&lt;")

        fancy_snippet = """
            </div> <!-- End of .entry-body-wrapper -->
            <pre class="prism"><code class="language-{snippet_language}">{code}</code></pre>
        """.format(snippet_language=snippet_language, code=code)

        # Return everything up until the slice, then the new and improved snippet, then everything after the slice ends
        return attr[:start_pos] + fancy_snippet + attr[snippet_end + self.code_delimiter_len:], fancy_snippet

