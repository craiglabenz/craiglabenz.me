# Python
import traceback
import time
import sys

# 3rd Party
try:
    from termcolor import cprint as _cprint
except ImportError:
    def _cprint(str, *args, **kwargs):
        print(str)

# Django
from django.conf import settings
from django.db import connection
# from django.http import Http404
# from django.shortcuts import redirect
from django.utils import timezone
from django.views.debug import technical_500_response

# Local Apps
from core.utils import colored_resp_time


class LogStuff(object):

    def process_request(self, request):
        querystring = ''
        if request.META['QUERY_STRING']:
            querystring = '?%s' % request.META['QUERY_STRING']
        cprint('%s %s %s%s' % (request.method, request.META.get('CONTENT_TYPE', ''), request.META.get('PATH_INFO', ''), querystring,), color='cyan')
        try:
            if request.method in ['POST', 'PUT'] and bool(request.body.decode('utf-8')):
                cprint(request.body.decode('utf-8'), color='cyan')
        except:
            # JSON errors are possible if the post data is weird, but whatever
            pass

    def process_exception(self, request, exception):
        cprint(traceback.format_exc(), color='red')

    def process_response(self, request, response):
        # if 'print_queries' not in request.GET.keys():
        #     return response

        try:
            import sqlparse
        except ImportError:
            sqlparse = None

        if len(connection.queries) > 0 and settings.DEBUG:
            total_time = 0.0
            for query in connection.queries:
                total_time = total_time + float(query['time'])
                continue
                print('')
                if sqlparse:
                    print(sqlparse.format(query['sql'], reindent=True))
                    print('\033[93m' + query['time'] + '\033[0m')
                else:
                    print(query['sql'])
                print('')
            print("\033[1;32m[TOTAL TIME: %s seconds]\033[0m" % total_time)
            print("  Ran %d queries" % len(connection.queries))
        return response


class LocalizeTimezone(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(request.user.get_timezone())
        else:
            timezone.deactivate()

    def process_response(self, request, response):
        timezone.deactivate()
        return response


class TimeRequests(object):

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            resp_time_ms = (time.time() - request._start_time) * 1000

            if settings.DEBUG:
                print('Responded in %s ms' % (colored_resp_time(resp_time_ms),))
        return response


def cprint(*args, **kwargs):
    if settings.TESTING:
        return

    if settings.DEBUG:
        _cprint(*args, **kwargs)
    else:
        pass
        # logger.debug()


class UserBasedExceptionMiddleware(object):
    """
    If request user is staff then display DEBUG information for 500 error
    """
    def process_exception(self, request, exception):
        if "see_raw" not in request.GET and request.user.is_authenticated() and request.user.is_staff and request.user.is_active:
            return technical_500_response(request, *sys.exc_info())
        return None
