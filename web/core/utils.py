import datetime
import hashlib
import logging
import re
import socket
import termcolor
import time
from markdown import markdown as _markdown

# Django
from django.conf import settings


def site_url(uri='', subdomain=''):
    """
    Handles the fact that ports are annoying.
    """
    if subdomain:
        subdomain = subdomain + '.'

    if settings.SITE_PORT in ['80', '443']:
        return '%s://%s%s%s' % (settings.SITE_PROTOCOL, subdomain, settings.SITE_HOST, uri,)
    else:
        return '%s://%s%s:%s%s' % (settings.SITE_PROTOCOL, subdomain, settings.SITE_HOST, settings.SITE_PORT, uri,)


def colored_resp_time(resp_time):
    """
    For stdout (either management commands or the dev server). Colors the
    supplied `resp_time` based on rules of speed.

    Args:
    @resp_time   int    The milliseconds it took for some request to come back.
    """
    resp_time = round(float(resp_time), 3)
    if resp_time < 200.0:
        color = 'green'
    elif resp_time < 500.0:
        color = 'yellow'
    else:
        color = 'red'
    return termcolor.colored(resp_time, color=color)


class RFC5424Filter(logging.Filter):

    """
    Adds a properly formatted time for use in syslog logging. Also adds the
    hostname and the local application name. The application name is used by
    rsyslog routing rules to get log messages to the right files.
    """

    def __init__(self, *args, **kwargs):
        self._tz_fix = re.compile(r'([+-]\d{2})(\d{2})$')
        super(RFC5424Filter, self).__init__(*args, **kwargs)

    def filter(self, record):
        try:
            record.hostname = socket.gethostname()
        except:
            record.hostname = '-'

        # This is here to avoid importing settings within the settings file
        from django.conf import settings
        record.app_name = 'sp-%s-%s' % (settings.APP_ENVIRONMENT, settings.NODE_TYPE)

        isotime = datetime.datetime.fromtimestamp(record.created).isoformat()
        tz = self._tz_fix.match(time.strftime('%z'))
        if time.timezone and tz:
            (offset_hrs, offset_min) = tz.groups()
            isotime = '{0}{1}:{2}'.format(isotime, offset_hrs, offset_min)
        else:
            isotime = isotime + 'Z'

        record.isotime = isotime

        return True


def smoosh_args(*args, **kwargs):
    key_suffix = ''
    prepared_args = []
    prepared_kwargs = []
    for arg in args:
        prepared_args.append(str(arg))

    for key, value in kwargs.items():
        prepared_kwargs.append('%s=%s' % (key, str(value),))

    all_prepared_args = prepared_args + prepared_kwargs
    if all_prepared_args:
        key_suffix = ';'.join(all_prepared_args)

    return key_suffix


def zero_pad(s, length):
    s = str(s)
    while len(s) < length:
        s = "0" + s

    return s


code_delimiter = "|||"
code_delimiter_len = len(code_delimiter)
vulnerable_languages = ["markup", "xml"]


def markdown(attr):

    snippet_hash_map = {}

    while "|||" in attr:
        attr, most_recent_snippet = parse_code_block(attr)

        snippet_hash = hashlib.md5(most_recent_snippet.encode('utf-8')).hexdigest()
        snippet_hash_map[snippet_hash] = most_recent_snippet

        print(snippet_hash)
        attr = attr.replace(most_recent_snippet, snippet_hash)

        if not attr.endswith(snippet_hash):
            fancier_snippet = snippet_hash + """\n<div class="entry-body-wrapper">"""
            attr = attr.replace(snippet_hash, fancier_snippet)

    marked_down = _markdown(attr)

    for key, value in snippet_hash_map.items():
        marked_down = marked_down.replace(key, value)

    return marked_down


def parse_code_block(attr):
    start_pos = attr.find(code_delimiter)
    next_newline_pos = attr[code_delimiter_len + start_pos:].find("\n") + start_pos + code_delimiter_len

    # Snippet language
    snippet_language = attr[start_pos + code_delimiter_len:next_newline_pos - 1]

    # Capture all the code
    snippet_end = attr[next_newline_pos:].find("|||") + next_newline_pos
    code = attr[next_newline_pos + 1:snippet_end]

    # Handle language-specific prism gotchas
    print('snippet_language', snippet_language)
    if snippet_language in vulnerable_languages:
        code = code.replace("<", "&lt;")

    fancy_snippet = """
        </div> <!-- End of .entry-body-wrapper -->
        <pre class="prism"><code class="language-{snippet_language}">{code}</code></pre>
    """.format(snippet_language=snippet_language, code=code)

    # Return everything up until the slice, then the new and improved snippet, then everything after the slice ends
    return attr[:start_pos] + fancy_snippet + attr[snippet_end + code_delimiter_len:], fancy_snippet
