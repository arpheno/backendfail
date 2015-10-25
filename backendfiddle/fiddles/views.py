from django.shortcuts import render
# Create your views here.
from django.views.generic import View, DetailView, UpdateView, ListView, CreateView
from httpproxy.views import HttpProxy

from fiddles.models import Fiddle, FiddleFile


class DynProxyView(HttpProxy):
    def get_object(self):
        return Fiddle.objects.get(pk=self.kwargs['pk'])
    rewrite = True
    @property
    def base_url(self):
        url= self.request.scheme+"://localhost:" + str(self.get_object().port)
        print url
        return url
    def get_full_url(self, url):
        result = super(DynProxyView, self).get_full_url(url)
        print result
        return result[:-1]


class EditFile(UpdateView):
    model = FiddleFile
    fields = ["content"]
    def get_object(self, queryset=None):
        return Fiddle.objects.get(pk=self.kwargs['pk']).fiddlefile_set.get(path=self.kwargs['path'])
class FiddleView(DetailView):
    model = Fiddle
class FiddleList(ListView):
    model = Fiddle
class CreateFiddle(CreateView):
    model = Fiddle
class RestartView(DetailView):
    model = Fiddle
    def get(self, request, *args, **kwargs):
        self.get_object().cleanup()
        self.get_object().spawn()
        return super(RestartView, self).get(request, *args, **kwargs)
class StopView(DetailView):
    model = Fiddle
    def get(self, request, *args, **kwargs):
        self.get_object().cleanup()
        return super(StopView, self).get(request, *args, **kwargs)
class LaunchView(DetailView):
    model = Fiddle
    def get(self, request, *args, **kwargs):
        self.get_object().spawn()
        return super(LaunchView, self).get(request, *args, **kwargs)
