import time
from contextlib import contextmanager
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, DetailView, UpdateView, CreateView, \
    TemplateView, DeleteView
from fabric.operations import local
from fiddles.helpers import suppress, copy_object, LoginRequiredMixin, rewrite_redirect, \
    CacheMixin
from fiddles.models import Fiddle, FiddleFile
from fiddles import models
from dj import models as djmodels
from revproxy.views import ProxyView
from ror import models as rormodels


@contextmanager
def container(fiddle):
    """Encapsulate startup and cleanup tasks for the container"""
    fiddle.spawn()
    yield
    fiddle.cleanup()


class DynProxyView(ProxyView):
    """ This is where the magic happens """
    retries = 10

    @method_decorator(csrf_exempt)
    def dispatch(self, request, path, *args, **kwargs):
        """
        The parent implementation is to proxy the request and return it from the
        upstream server."""
        # with container(self.get_object()):
        response = None
        with container(self.get_object()):
            self.upstream = self.base_url
            for _ in range(15):
                try:
                    if path and path[0] == "/":
                        path = path[1:]
                    response = super(DynProxyView, self).dispatch(request, path)
                    if "location" in response._headers:
                        response._headers["location"] = rewrite_redirect(response,
                                                                         request)
                    break
                except:
                    time.sleep(1)
            self.get_object().cleanup()
        if not response:
            return HttpResponse(
                "Your app failed to boot, perhaps there is a syntax error in your code.")
        return response

    def get_object(self):
        """ :return: The appropriate Fiddle instance with the correct class """
        return Fiddle.objects.select_subclasses().get(pk__startswith=self.kwargs['pk'])

    @property
    def base_url(self):
        """ Overriding parent behaviour to get dynamic proxying """
        ip = local("netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'", capture=True)
        if "10.0" in ip:
            ip = "localhost"
        url = "http://" + ip + ":" + str(self.get_object().port)
        return url


class FiddleView(DetailView):
    model = Fiddle
    template_name = 'fiddles/fiddle_detail.html'


class FiddleList(TemplateView):
    template_name = "fiddles/fiddle_list.html"


class CreateFiddle(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous():
            self.object = self.model_class.objects.create(owner=request.user)
        else:
            self.object = self.model_class.objects.create()
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
            "pk"  : self.object.id[:8],
            "path": self.object.entrypoint
        }
        return reverse_lazy("file-edit", kwargs=kwargs)


class CopyMixin(object):
    def get(self, request, *args, **kwargs):
        if self.copy_on_write():
            self.create_copy()
            return redirect(self.get_success_url())
        return super(CopyMixin, self).get(request, *args, **kwargs)

    def create_copy(self):
        result = copy_object(self.get_fiddle())
        if not self.request.user.is_anonymous():
            result.owner = self.request.user
            result.save()
        self.object = result.fiddlefile_set.get(path=self.get_object().path)


class FiddleFileMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.fiddle = self.get_fiddle()
        if not self.owner and not request.user.is_anonymous():
            fiddle = self.get_fiddle()
            fiddle.owner = request.user
            fiddle.save()
        return super(FiddleFileMixin, self).dispatch(request, *args, **kwargs)

    @property
    def owner(self):
        return self.get_fiddle().owner

    def get_fiddle(self):
        return Fiddle.objects.get_subclass(pk__startswith=self.kwargs['pk'])

    def copy_on_write(self):
        if not self.owner:
            return False
        if self.request.user.is_anonymous():
            return True
        if not self.request.user == self.owner:
            return True

    def post(self, request, *args, **kwargs):
        if self.copy_on_write():
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
            "pk"  : self.object.id[:8],
            "path": self.object.path
        }
        return reverse_lazy('file-edit', kwargs=kwargs)


class EditFile(CopyMixin, FiddleFileMixin, UpdateView):
    model = FiddleFile
    fields = ["content"]
    template_name = "fiddles/fiddlefile_edit.html"


class CreateFile(FiddleFileMixin, CreateView):
    model = FiddleFile
    fields = ["path"]

    def form_valid(self, form):
        # We have to attach the owner.
        self.object = form.save(commit=False)
        self.object.fiddle = self.get_fiddle()
        self.object.save()
        self.kwargs['path'] = self.object.path

        return redirect(self.get_success_url())


class RenameFile(FiddleFileMixin, UpdateView):
    model = FiddleFile
    fields = ["path"]


class DeleteFile(FiddleFileMixin, DeleteView):
    model = FiddleFile


class ViewFile(FiddleFileMixin, DetailView):
    model = FiddleFile
