from django.urls import path
from .views import index
from . import urls_htmx


urlpatterns = [
    path('', index, name='index'),
]



urlpatterns += urls_htmx.htmx_url_patterns
