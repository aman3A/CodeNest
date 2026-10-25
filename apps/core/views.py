from django.views.generic import ListView

from apps.posts.models import Post


class HomeView(ListView):
	model = Post
	template_name = "core/home.html"
	context_object_name = "posts"
	paginate_by = 6

	def get_queryset(self):
		return Post.objects.filter(status=Post.Status.PUBLISHED).select_related(
			"author", "category"
		)
from django.shortcuts import render

# Create your views here.
