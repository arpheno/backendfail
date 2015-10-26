from django.conf.urls import include, url
from django.views.generic import DetailView

from fiddles.views import DynProxyView,  FiddleView, EditFile,  CreateFiddle, ViewFile, CopyFiddle

""" All these are polymorphic and should work for all kinds of fiddles """




urlpatterns = [
    # Create
    url(r'^new/(?P<class>[-\w]+)/?$', CreateFiddle.as_view(), name="fiddle-create"),
    url(r'^copy/(?P<pk>[-\w]+)/?$', CopyFiddle.as_view(), name="fiddle-copy"),
    # Detail
    url(r'^(?P<pk>[-\w]+)/?$', FiddleView.as_view(), name="fiddle-detail"),
    # Control views
    url(r'^(?P<pk>[-\w]+)/result/(?P<url>.*)$', DynProxyView.as_view(), name='result'),
    url(r'^(?P<pk>[-\w]+)/(?P<path>.+)/edit/?$', EditFile.as_view(),name='file-edit'),
    url(r'^(?P<pk>[-\w]+)/(?P<path>.+)/?$', ViewFile.as_view(),name="file-view"),
]
