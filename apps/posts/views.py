from django.views.generic import DetailView

from .models import Post


class PostDetailView(DetailView):
	model = Post
	template_name = "posts/post_detail.html"
	context_object_name = "post"

	def get_queryset(self):
		return Post.objects.filter(status=Post.Status.PUBLISHED).select_related(
			"author", "category"
		)
from django.shortcuts import render

# Create your views here.
