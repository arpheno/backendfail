from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic import View, DetailView, UpdateView, ListView, CreateView
from httpproxy.views import HttpProxy

from fiddles.models import Fiddle, FiddleFile
from fiddles import models
from dj import models as djmodels

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
class FiddleMixin(object):
    def get_queryset(self):
        return super(FiddleMixin, self).get_queryset().select_subclasses()

class EditFile(FiddleMixin,UpdateView):
    model = FiddleFile
    fields = ["content"]
    def get_object(self, queryset=None):
        return Fiddle.objects.get(pk=self.kwargs['pk']).fiddlefile_set.get(path=self.kwargs['path'])
class FiddleView(FiddleMixin,DetailView):
    model = Fiddle
    template_name = 'fiddles/fiddle_detail.html'
class FiddleList(FiddleMixin,ListView):
    model = Fiddle
class CreateFiddle(FiddleMixin,CreateView):
    fields = ["name"]
    @property
    def model(self):
        try:
            return getattr(models,self.kwargs["class"])
        except:
            return getattr(djmodels,self.kwargs["class"])
    def get_success_url(self):
        return reverse_lazy("fiddle-detail",kwargs={"pk":self.object.id})
class RestartView(FiddleMixin,DetailView):
    model = Fiddle
    def get(self, request, *args, **kwargs):
        self.get_object().cleanup()
        self.get_object().spawn()
        return redirect(reverse_lazy('result',kwargs={"pk":self.get_object().id,"url":""}))
class StopView(FiddleMixin,DetailView):
    model = Fiddle
    def get(self, request, *args, **kwargs):
        self.get_object().cleanup()
        return redirect(reverse_lazy("fiddle-detail",kwargs={"pk":self.get_object.id}))
class LaunchView(FiddleMixin,DetailView):
    model = Fiddle
    def get(self, request, *args, **kwargs):
        self.get_object().spawn()
        return redirect(reverse_lazy('result',kwargs={"pk":self.get_object().id,"url":""}))
