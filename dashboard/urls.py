from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^portfoliojson$', views.portfoliojson, name='portfolio'),
    url(r'^frontierjson$', views.frontierjson, name='frontier'),
    url(r'^relativefrontjson$', views.relativefrontjson, name='relfrontier'),
    url(r'^allocationjson$', views.allocationjson, name='allocation'),
    url(r'^spkperformancejson$', views.spkperformancejson, name='Sparkline Performance'),
]