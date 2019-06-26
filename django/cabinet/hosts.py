from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'app', 'bot.urls', name='app'),
)
