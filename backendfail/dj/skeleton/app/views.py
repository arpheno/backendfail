"""
In Django, a view is an endpoint that can be accessed by any
client to retrieve data over the wire. For example, some views
serve data rendered with a template to a web server
that in turn serves the HTML page to a client.
While other views serve JSON data to a web server and these views become
part of a RESTful API.
"""
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
# Create your views here.
from django.views.generic import CreateView, ListView
from app.models import Blog
from django.http import HttpResponse


# The simplest possible view in django. It returns HTML when called via urls.py
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


# A class based view that creates Blog instances in the database
class BlogCreateView(CreateView):
    model = Blog
    fields = ['name']
    template_name = "app/blog_create.html"

    def get_success_url(self):
        return reverse_lazy('blog-list')


# A class based view that lists all blogs in the database
class BlogListView(ListView):
    model = Blog
    template_name = "app/blog_list.html"
