# Local Settings
from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG


MIDDLEWARE_CLASSES += (
    'core.middleware.TimeRequests',
    'core.middleware.LogStuff',
)

try:
    from .override import *
except ImportError:
    pass
