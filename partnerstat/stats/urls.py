from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/', views.search, name='search'),
    url(r'^users_json/', views.user_list_json, name='user_list_json'),
    url(r'^views_json/', views.user_views_json, name='user_views_json'),
    url(r'^users/(?P<id>[0-9]+)', views.user_details, name='user_details'),
    url(r'^users/', views.user_list, name='user_list'),
]