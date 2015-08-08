import datetime
import logging
import re
import socket
import termcolor
import time

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
