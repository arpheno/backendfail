from django.conf.urls import include, url

from fiddles.views import DynProxyView, LaunchView, FiddleView, EditFile, RestartView, StopView, CreateFiddle

urlpatterns = [
    url(r'^new/?$', CreateFiddle.as_view(),name="create-fiddle"),
    url(r'^(?P<pk>[-\w]+)/launch/?$', LaunchView.as_view(),name='start'),
    url(r'^(?P<pk>[-\w]+)/stop/?$', StopView.as_view(),name='stop'),
    url(r'^(?P<pk>[-\w]+)/result/(?P<url>.*)$', DynProxyView.as_view(),name='result'),
    url(r'^(?P<pk>[-\w]+)/restart/?$', RestartView.as_view(),name='restart'),
    url(r'^(?P<pk>[-\w]+)/?$', FiddleView.as_view(),name="fiddle-detail"),
    url(r'^(?P<pk>[-\w]+)/(?P<path>.+)?$', EditFile.as_view()),
]
