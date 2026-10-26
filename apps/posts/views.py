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
from io import BytesIO
from urllib.parse import urljoin
from uuid import uuid4

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from PIL import Image, UnidentifiedImageError

from .models import Post


MAX_EDITOR_IMAGE_SIZE = 5 * 1024 * 1024
MAX_EDITOR_IMAGE_PIXELS = 25_000_000
EDITOR_IMAGE_FORMATS = {
	"JPEG": ".jpg",
	"PNG": ".png",
	"WEBP": ".webp",
}


class PostDetailView(DetailView):
	model = Post
	template_name = "posts/post_detail.html"
	context_object_name = "post"

	def get_queryset(self):
		return Post.objects.filter(status=Post.Status.PUBLISHED).select_related(
			"author", "category"
		)


@staff_member_required
@require_POST
def upload_editor_image(request):
	uploaded_file = request.FILES.get("image")
	if uploaded_file is None:
		return JsonResponse({"error": "Choose an image to upload."}, status=400)
	if uploaded_file.size > MAX_EDITOR_IMAGE_SIZE:
		return JsonResponse(
			{"error": "Images must be no larger than 5 MB."},
			status=413,
		)

	try:
		uploaded_file = forms.ImageField().clean(uploaded_file)
	except ValidationError:
		return JsonResponse({"error": "The uploaded file is not a valid image."}, status=400)

	try:
		with Image.open(uploaded_file) as image:
			image_format = image.format
			if image_format not in EDITOR_IMAGE_FORMATS:
				return JsonResponse(
					{"error": "Use a JPEG, PNG, or WebP image."},
					status=400,
				)
			if image.width * image.height > MAX_EDITOR_IMAGE_PIXELS:
				return JsonResponse(
					{"error": "The image dimensions are too large."},
					status=400,
				)
			image.load()
			if image_format == "JPEG":
				image = image.convert("RGB")
			elif image.mode not in {"RGB", "RGBA"}:
				image = image.convert("RGBA")
			image_data = BytesIO()
			image.save(image_data, format=image_format)
	except (Image.DecompressionBombError, OSError, UnidentifiedImageError, ValueError):
		return JsonResponse({"error": "The uploaded image could not be processed."}, status=400)

	extension = EDITOR_IMAGE_FORMATS[image_format]
	image_data.seek(0)
	image_path = default_storage.save(
		f"editor_images/{uuid4().hex}{extension}",
		ContentFile(image_data.read()),
	)
	image_url = urljoin(request.build_absolute_uri("/"), default_storage.url(image_path))
	return JsonResponse({"url": image_url})
