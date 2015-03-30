"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""


import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seqstats.settings")

path = '/n/informatics/iggy/IggyTools/iggytools/iggyapp'
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()



