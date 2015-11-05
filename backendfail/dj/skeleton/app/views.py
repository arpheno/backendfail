from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
# Create your views here.
from django.views.generic import CreateView, ListView

from app.models import Blog


class BlogCreateView(CreateView):
    model = Blog
    fields = ['name']
    template_name = "app/blog_create.html"

    def get_success_url(self):
        return reverse_lazy('blog-list')


class BlogListView(ListView):
    model = Blog
    template_name = "app/blog_list.html"
