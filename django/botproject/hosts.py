from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'cabinet', 'cabinet.urls', name='app'),
    # host(r'partner', 'partners.urls', name='partners'),
)
