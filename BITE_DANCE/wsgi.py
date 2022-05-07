"""
WSGI config for BITE_DANCE project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#from whitenoise import WhiteNoise
#from static_ranges import Ranges
#from dj_static import Cling, MediaCling

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BITE_DANCE.settings')
application = get_wsgi_application()
#application = WhiteNoise(application)
#application = Ranges(Cling(MediaCling(application)))



#application = get_wsgi_application()
