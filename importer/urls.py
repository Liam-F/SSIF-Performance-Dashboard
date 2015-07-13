from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^prices$', views.index, name='prices'),
    url(r'^confirm/$', views.confirm, name='confirm'),
]