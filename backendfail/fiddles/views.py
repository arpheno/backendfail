import time
from contextlib import contextmanager

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
from fiddles.helpers import suppress, copy_fiddle
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


@contextmanager
def container(fiddle):
    """Encapsulate startup and cleanup tasks for the container"""
    fiddle.spawn()
    yield
    fiddle.cleanup()


class DynProxyView(FiddleMixin, ProxyView):
    """ This is where the magic happens """
    retries = 10

    @method_decorator(csrf_exempt)
    def dispatch(self, request, path, *args, **kwargs):
        """
        The parent implementation is to proxy the request and return it from the
        upstream server."""
        # with container(self.get_object()):
        self.get_object().spawn()
        self.upstream = self.base_url
        while True:
            try:
                if path and path[0] == "/":
                    path = path[1:]
                response = super(DynProxyView, self).dispatch(request, path)
                if "location" in response._headers:
                    response._headers["location"] = self.rewrite_redirect(response,
                                                                          request)
                break
            except:
                time.sleep(1)
        self.get_object().cleanup()
        return response

    def rewrite_redirect(self, response, request):
        """ Oh god, the aweful."""
        location = response._headers["location"][1]
        location = location[location.find("//") + 3:]
        path = location[location.find("/"):]
        base = request.build_absolute_uri()
        base = base[:base.find("t//") + 2]
        return 'Location', base + path + "/"

    def get_object(self):
        """ :return: The appropriate Fiddle instance with the correct class """
        return Fiddle.objects.select_subclasses().get(pk=self.kwargs['pk'])

    @property
    def base_url(self):
        """ Overriding parent behaviour to get dynamic proxying """
        ip = local("netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'", capture=True)
        if "10.0" in ip:
            ip = "localhost"
        url = "http://" + ip + ":" + str(self.get_object().port)
        return url


class FiddleView(FiddleMixin, DetailView):
    model = Fiddle
    template_name = 'fiddles/fiddle_detail.html'


class FiddleList(TemplateView):
    template_name = "fiddles/fiddle_list.html"


class CreateFiddle(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = self.model_class.objects.create(owner=request.user)
        return redirect(self.get_success_url())

    @property
    def model_class(self):
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


class FiddleFileMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.fiddle = self.get_fiddle()
        return super(FiddleFileMixin, self).dispatch(request, *args, **kwargs)

    def get_fiddle(self):
        return Fiddle.objects.get_subclass(pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        if not self.request.user == self.get_fiddle().owner:
            raise PermissionDenied
        return super(FiddleFileMixin, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.get_fiddle().fiddlefile_set.get(path=self.kwargs['path'])

    def get_context_data(self, **kwargs):
        context = super(FiddleFileMixin, self).get_context_data(**kwargs)
        context['file_content'] = self.get_object().content
        return context

    def get_success_url(self):
        kwargs = {
            "pk"  : self.object.id,
            "path": self.kwargs['path']
        }
        return reverse_lazy('file-edit', kwargs=kwargs)


class EditFile(LoginRequiredMixin, FiddleFileMixin, UpdateView):
    model = FiddleFile
    fields = ["content"]
    template_name = "fiddles/fiddlefile_edit.html"

    def get(self, request, *args, **kwargs):
        if not self.request.user == self.get_fiddle().owner:
            # if it doesn't belong to the user we create a new fiddle.
            self.create_copy()
            return redirect(self.get_success_url())
        return super(EditFile, self).get(request, *args, **kwargs)

    def create_copy(self):
        result = copy_fiddle(self.get_fiddle())
        result.owner = self.request.user
        result.save()
        self.object = result


class ViewFile(FiddleFileMixin, DetailView):
    model = FiddleFile
    template_name = "fiddles/fiddlefile_view.html"


class CreateFile(LoginRequiredMixin, FiddleFileMixin, CreateView):
    model = FiddleFile
    fields = ["path"]

    template_name = "fiddles/fiddlefile_form.html"

    def form_valid(self, form):
        # We have to attach the owner.
        self.object = form.save(commit=False)
        self.object.fiddle = self.get_fiddle()
        self.object.save()
        return redirect(
            reverse_lazy('file-edit',
                         kwargs={"pk": self.kwargs['pk'], "path": self.object.path}))


class RenameFile(LoginRequiredMixin, FiddleFileMixin, UpdateView):
    model = FiddleFile
    fields = ["path"]

    template_name = "fiddles/fiddlefile_form.html"


class DeleteFile(LoginRequiredMixin, DeleteView):
    model = FiddleFile

    def get_success_url(self):
        return reverse_lazy('fiddle-detail', kwargs={"pk": self.kwargs['pk']})
