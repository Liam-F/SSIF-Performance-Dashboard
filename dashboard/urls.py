from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^portfoliojson$', views.portfoliojson, name='portfolio'),
    url(r'^frontierjson$', views.frontierjson, name='frontier'),
    url(r'^allocationjson$', views.allocationjson, name='allocation'),
]