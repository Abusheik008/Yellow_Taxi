
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('compute/', compute, name='compute'),
    path('', home, name='home'),
    path('dashboard/', dashboard)
] + static(settings.STATIC_URL, document_root='./static/', )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL_DATA, document_root=settings.MEDIA_ROOT_DATA)
