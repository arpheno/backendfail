from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from app.views import BlogListView, BlogCreateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='app/app.html')),
    url(r'^blogs/new/?$', BlogCreateView.as_view(), name='blog-create'),
    url(r'^blogs/?$', BlogListView.as_view(), name='blog-list'),
]
