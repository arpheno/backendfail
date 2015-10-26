from django.conf.urls import include, url

from fiddles.views import DynProxyView, LaunchView, FiddleView, EditFile, RestartView, StopView, CreateFiddle

""" All these are polymorphic and should work for all kinds of fiddles """
urlpatterns = [
    #Create
    url(r'^new/(?P<class>[-\w]+)/?$', CreateFiddle.as_view(),name="create-fiddle"),
    #Detail
    url(r'^(?P<pk>[-\w]+)/?$', FiddleView.as_view(),name="fiddle-detail"),
    #Control views
    url(r'^(?P<pk>[-\w]+)/launch/?$', LaunchView.as_view(),name='start'),
    url(r'^(?P<pk>[-\w]+)/stop/?$', StopView.as_view(),name='stop'),
    url(r'^(?P<pk>[-\w]+)/restart/?$', RestartView.as_view(),name='restart'),
    #Wildcard views
    url(r'^(?P<pk>[-\w]+)/result/(?P<url>.*)$', DynProxyView.as_view(),name='result'),
    url(r'^(?P<pk>[-\w]+)/(?P<path>.+)?$', EditFile.as_view()),
]
