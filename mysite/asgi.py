"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
# https://stackoverflow.com/questions/53683806/django-apps-arent-loaded-yet-when-using-asgi
django_asgi_app = get_asgi_application()

# from django.core.asgi import get_asgi_application
import polls.routing
from polls.middleware import TokenAuthMiddleware


# application = get_asgi_application()

application = ProtocolTypeRouter({
# http请求使用这个
"http": django_asgi_app,

# websocket请求使用这个
"websocket": TokenAuthMiddleware(
        URLRouter(
            polls.routing.websocket_urlpatterns
        )
    ),
})
# daphne -p 8000 mysite.asgi:application