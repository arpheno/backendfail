import time

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, DetailView, UpdateView, CreateView, \
    TemplateView, DeleteView
from fabric.operations import local

from fiddles.helpers import suppress
from fiddles.models import Fiddle, FiddleFile
from fiddles import models
from dj import models as djmodels
from revproxy.views import ProxyView
from ror import models as rormodels


class FiddleMixin(object):
    """ Mixin to provide polymorphism via `select_subclasses` """

    def get_queryset(self):
        return super(FiddleMixin, self).get_queryset().select_subclasses()


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class DynProxyView(FiddleMixin, ProxyView):
    """ This is where the magic happens """
    retries = 10

    @method_decorator(csrf_exempt)
    def dispatch(self, request, path, *args, **kwargs):
        """
        The parent implementation is to proxy the request and return it from the
        upstream server.
        Before we start proxying, we have to run the docker container and start it,
        perform startup tasks and wait for these to finish. This takes some time so
        we wait a few seconds.
        After the request has been processed we call the cleanup method, which takes
        care of either destroying or stopping the container. """
        self.get_object().spawn()
        self.upstream = self.base_url

        while True:
            try:
                print path
                if path and path[0] == "/":
                    path = path[1:]
                result = super(DynProxyView, self).dispatch(request, path)
                if "location" in result._headers:
                    location = result._headers["location"][1]
                    location = location[location.find("//") + 3:]
                    path = location[location.find("/"):]
                    base = request.build_absolute_uri()
                    base = base[:base.find("t//") + 2]
                    print base, path
                    result._headers["location"] = ('Location', base + path + "/")
                break
            except:
                print self.base_url
                time.sleep(1)
        self.get_object().cleanup()
        return result

    def get_object(self):
        """
        :return: The appropriate Fiddle instance with the correct class
        """
        return Fiddle.objects.select_subclasses().get(pk=self.kwargs['pk'])

    @property
    def base_url(self):
        """ Overriding parent behaviour to get dynamic proxying """
        ip = local("netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'", capture=True)
        if "10.0" in ip:
            ip = "localhost"
        url = "http://" + ip + ":" + str(self.get_object().port)
        return url


class EditFile(LoginRequiredMixin, FiddleMixin, UpdateView):
    model = FiddleFile
    fields = ["content"]
    template_name = "fiddles/fiddlefile_edit.html"

    def dispatch(self, request, *args, **kwargs):
        self.fiddle = self.get_fiddle()
        return super(EditFile, self).dispatch(request, *args, **kwargs)

    def get_fiddle(self):
        return Fiddle.objects.get_subclass(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(EditFile, self).get_context_data(**kwargs)
        context['file_content'] = self.get_object().content
        return context

    def post(self, request, *args, **kwargs):
        if not self.request.user == self.get_object().fiddle.owner:
            raise PermissionDenied
        return super(EditFile, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not self.request.user == self.fiddle.owner:
            # if it doesn't belong to the user we create a new fiddle.
            result = self.copy_fiddle()
            return redirect(reverse_lazy('file-edit',
                                         kwargs={"pk"  : result.id,
                                                 "path": self.kwargs['path']}))
        return super(EditFile, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.fiddle.fiddlefile_set.get(path=self.kwargs['path'])

    def copy_fiddle(self):
        self.fiddle.id = None
        self.fiddle.pk = None
        self.fiddle.owner = self.request.user
        self.fiddle.save()
        for file in self.get_fiddle().fiddlefile_set.all():
            file.id = None
            file.pk = None
            file.fiddle = self.fiddle
            file.save()
        return self.fiddle


class ViewFile(FiddleMixin, DetailView):
    model = FiddleFile
    template_name = "fiddles/fiddlefile_view.html"

    def get_context_data(self, **kwargs):
        context = super(ViewFile, self).get_context_data(**kwargs)
        context['file_content'] = self.get_object().content
        return context

    def get_object(self, queryset=None):
        return Fiddle.objects.get(pk=self.kwargs['pk']).fiddlefile_set.get(
            path=self.kwargs['path'])


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
        with suppress(Exception):
            return getattr(models, self.kwargs["class"])
        with suppress(Exception):
            return getattr(djmodels, self.kwargs["class"])
        with suppress(Exception):
            return getattr(rormodels, self.kwargs["class"])

    def get_success_url(self):
        kwargs = {
            "pk"  : self.object.id,
            "path": self.object.entrypoint
        }
        return reverse_lazy("file-edit", kwargs=kwargs)


class CreateFile(LoginRequiredMixin, CreateView):
    model = FiddleFile
    fields = ["path"]

    template_name = "fiddles/fiddlefile_form.html"

    def get_context_data(self, **kwargs):
        context = super(CreateFile, self).get_context_data(**kwargs)
        context['object'] = self.get_fiddle().fiddlefile_set.first()
        return context

    def dispatch(self, request, *args, **kwargs):
        self.fiddle = self.get_fiddle()
        return super(CreateFile, self).dispatch(request, *args, **kwargs)

    def get_fiddle(self):
        return Fiddle.objects.get_subclass(pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        if not self.request.user == self.fiddle.owner:
            raise PermissionDenied
        return super(CreateFile, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.fiddle = self.get_fiddle()
        obj.save()
        return redirect(
            reverse_lazy('file-edit', kwargs={"pk": self.kwargs['pk'], "path": obj.path}))


class RenameFile(LoginRequiredMixin, UpdateView):
    model = FiddleFile
    fields = ["path"]

    template_name = "fiddles/fiddlefile_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.fiddle = self.get_fiddle()
        if not self.request.user == self.fiddle.owner:
            raise PermissionDenied
        return super(RenameFile, self).dispatch(request, *args, **kwargs)

    def get_fiddle(self):
        return Fiddle.objects.get_subclass(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('file-edit',
                            kwargs={"pk": self.kwargs['pk'], "path": self.object.path})


class DeleteFile(LoginRequiredMixin, DeleteView):
    model = FiddleFile

    def dispatch(self, request, *args, **kwargs):
        self.fiddle = self.get_fiddle()
        if not self.request.user == self.fiddle.owner:
            raise PermissionDenied
        return super(DeleteFile, self).dispatch(request, *args, **kwargs)

    def get_fiddle(self):
        return Fiddle.objects.get_subclass(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('fiddle-detail', kwargs={"pk": self.kwargs['pk']})
