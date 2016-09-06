from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^stats/', include('stats.urls')),
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
]