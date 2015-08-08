# System
import re

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

        # This is our global pattern
        pattern = r'-s-[\w\-]+-'

        while True:
            # Are there anymore matches?
            matches = re.search(pattern, attr)
            if matches is None:
                # Bail if not, of course
                break

            # Pull out the exact string that matched
            match = matches.group()

            # Extract the snippet's PK from the match
            snippet_slug_match = match[3:-1]

            # Get that snippet
            snippet = obj.snippets_dict[snippet_slug_match]

            # Run a very simple replace of the match and its
            # ultimate highlighted code
            fancy_snippet = """
                </div> <!-- End of .entry-body-wrapper -->
                <pre class="prism"><code class="language-{snippet_language}">{code}</code></pre>
            """.format(
                snippet_language=snippet.language.prism_tag,
                code=snippet.get_prepared_code()
            )
            attr = attr.replace(match, fancy_snippet)

            if not attr.endswith(fancy_snippet):
                fancier_snippet = fancy_snippet + """\n<div class="entry-body-wrapper">"""
                attr = attr.replace(fancy_snippet, fancier_snippet)

        # Once the loop breaks, we're good
        return attr

# register.tag('render_with_snippets', do_render_with_snippets)


def find_str(s, char):
    index = 0
    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index + len(char)] == char:
                    return index
            index += 1
    return -1
