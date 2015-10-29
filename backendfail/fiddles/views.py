import time
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic import View, DetailView, UpdateView, ListView, CreateView, TemplateView
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
        while True:
            try:
                result = super(DynProxyView, self).dispatch(request, url, *args, **kwargs)
                break
            except:
                time.sleep(1)
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
        url = "http://127.0.0.1:" + str(self.get_object().port)
        return url

    def get_full_url(self, url):
        """ There is a redundant slash at the end of the url, so we have to strip it """
        result = super(DynProxyView, self).get_full_url(url)
        return result[:-1]


class EditFile(LoginRequiredMixin, FiddleMixin, UpdateView):
    model = FiddleFile
    fields = ["content"]
    template_name = "fiddles/fiddlefile_edit.html"

    def get_context_data(self, **kwargs):
        context = super(EditFile, self).get_context_data(**kwargs)
        context['file_content'] = self.get_object().content
        return context
    def post(self, request, *args, **kwargs):
        if not self.request.user == self.get_object().fiddle.owner:
            raise PermissionDenied
        return super(EditFile, self).post(request,*args,**kwargs)
    def get(self, request, *args, **kwargs):
        if not self.request.user == self.get_object().fiddle.owner:
            # if it doesn't belong to the user we create a new fiddle.
            result = self.copy_fiddle(self.get_object())
            return redirect(reverse_lazy('file-edit',
                                         kwargs={"pk": result.id, "path": self.kwargs['path']}))
        return super(EditFile, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Fiddle.objects.get(pk=self.kwargs['pk']).fiddlefile_set.get(path=self.kwargs['path'])

    def copy_fiddle(self, obj):
        obj=obj.fiddle
        obj.id = None
        obj.owner = self.request.user
        obj.save()
        print obj.id
        for file in self.get_object().fiddle.fiddlefile_set.all():
            file.id = None
            file.fiddle = obj
            file.save()
        return obj


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


class FiddleList(TemplateView):
    template_name = "fiddles/fiddle_list.html"


class CreateFiddle(LoginRequiredMixin, View):
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
        return reverse_lazy("file-edit",
                            kwargs={"pk": self.object.id,
                                    "path":self.object.entrypoint})
