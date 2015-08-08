# Production Settings
from .base import *

with open('/etc/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()


ALLOWED_HOSTS = ['craiglabenz.me']


DEBUG = False
ENV = "production"
SITE_HOST = ALLOWED_HOSTS[0]
SITE_PORT = 80


STATIC_URL = 'http://craiglabenz.me/static/'
STATIC_ROOT = '/home/django/craigblog/web/collected_static/'
STATICFILES_DIRS = (
    BASE_DIR + '/static',
    BASE_DIR + '/media',
)


del TEMPLATES[0]['APP_DIRS']
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
