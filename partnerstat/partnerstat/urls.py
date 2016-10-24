from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from stats.views import index as stats_index

urlpatterns = [
    url(r'^$', stats_index),
    url(r'^login/$', login, name='login'),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^stats/', include('stats.urls')),
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
]