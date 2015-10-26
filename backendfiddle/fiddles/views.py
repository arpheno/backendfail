import time

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic import View, DetailView, UpdateView, ListView, CreateView
from httpproxy.views import HttpProxy
from fiddles.models import Fiddle, FiddleFile
from fiddles import models
from dj import models as djmodels


class FiddleMixin(object):
    """ Mixin to provide polymorphism via `select_subclasses` """

    def get_queryset(self):
        return super(FiddleMixin, self).get_queryset().select_subclasses()

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
class DynProxyView(FiddleMixin, HttpProxy):
    """ This is where the magic happens """

    def dispatch(self, request, url, *args, **kwargs):
        """
        The parent implementation is to proxy the request and return it from the upstream server.
        Before we start proxying, we have to run the docker container and start it,
        perform startup tasks and wait for these to finish. This takes some time so
        we wait a few seconds.
        After the request has been processed we call the cleanup method, which takes care of either
        destroying or stopping the container.
        """
        self.get_object().spawn()
        time.sleep(15)
        result = super(DynProxyView, self).dispatch(request, url, *args, **kwargs)
        self.get_object().cleanup()
        return result

    def get_object(self):
        """
        :return: The appropriate Fiddle instance with the correct class
        """
        return Fiddle.objects.select_subclasses().get(pk=self.kwargs['pk'])

    rewrite = True

    @property
    def base_url(self):
        """ Overriding parent behaviour to get dynamic proxying """
        url = self.request.scheme + "://localhost:" + str(self.get_object().port)
        return url

    def get_full_url(self, url):
        """ There is a redundant slash at the end of the url, so we have to strip it """
        result = super(DynProxyView, self).get_full_url(url)
        return result[:-1]


class EditFile(LoginRequiredMixin,FiddleMixin, UpdateView):
    model = FiddleFile
    fields = ["content"]
    template_name = "fiddles/fiddlefile_edit.html"

    def get_context_data(self, **kwargs):
        context = super(EditFile, self).get_context_data(**kwargs)
        context['file_content'] = self.get_object().content
        return context

    def get_object(self, queryset=None):
        return Fiddle.objects.get(pk=self.kwargs['pk']).fiddlefile_set.get(path=self.kwargs['path'])


class ViewFile(FiddleMixin, DetailView):
    model = FiddleFile
    template_name = "fiddles/fiddlefile_view.html"

    def get_context_data(self, **kwargs):
        context = super(ViewFile, self).get_context_data(**kwargs)
        context['file_content'] = self.get_object().content
        return context

    def get_object(self, queryset=None):
        return Fiddle.objects.get(pk=self.kwargs['pk']).fiddlefile_set.get(path=self.kwargs['path'])


class FiddleView(FiddleMixin, DetailView):
    model = Fiddle
    template_name = 'fiddles/fiddle_detail.html'


class FiddleList(FiddleMixin, ListView):
    model = Fiddle


class CreateFiddle(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        # TODO Maybe auth?
        self.object = self.get_model().objects.create(owner=self.request.user)
        return redirect(self.get_success_url())

    def get_model(self):
        """ Search for available subclasses of `Fiddle` """
        try:
            return getattr(models, self.kwargs["class"])
        except:
            return getattr(djmodels, self.kwargs["class"])

    def get_success_url(self):
        return reverse_lazy("fiddle-detail", kwargs={"pk": self.object.id})


class CopyFiddle(LoginRequiredMixin,FiddleMixin, DetailView):
    """ Copy a fiddle to allow someone to edit """
    def get(self, *args, **kwargs):
        self.copy_fiddle()
        return redirect(self.get_success_url())

    def copy_fiddle(self):
        obj = self.get_object()
        obj.id = None
        obj.owner = self.request.user
        obj.save()
        for file in self.get_object().fiddlefile_set.all():
            file.id = None
            file.fiddle = obj
            file.save()
        self.object = obj

    def get_success_url(self):
        return reverse_lazy("fiddle-detail", kwargs={"pk": self.object.id})
