from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.posts.models import Category, Post


class BlogPageTests(TestCase):
	def setUp(self):
		self.author = get_user_model().objects.create_user(
			username="writer", password="test-password-123"
		)

	def test_homepage_lists_published_posts_only(self):
		published = Post.objects.create(
			title="Published Python guide",
			slug="published-python-guide",
			author=self.author,
			content="A published tutorial.",
			status=Post.Status.PUBLISHED,
		)
		Post.objects.create(
			title="Private draft",
			slug="private-draft",
			author=self.author,
			content="Not for public readers.",
		)

		response = self.client.get(reverse("core:home"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, published.title)
		self.assertNotContains(response, "Private draft")

	def test_published_post_detail_is_visible(self):
		category = Category.objects.create(name="Python")
		post = Post.objects.create(
			title="A tutorial",
			slug="a-tutorial",
			author=self.author,
			category=category,
			content="Article body.",
			status=Post.Status.PUBLISHED,
		)

		response = self.client.get(reverse("posts:detail", args=[post.slug]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Article body.")

	def test_draft_post_detail_returns_404(self):
		post = Post.objects.create(
			title="Unpublished",
			slug="unpublished",
			author=self.author,
			content="Draft body.",
		)

		response = self.client.get(reverse("posts:detail", args=[post.slug]))

		self.assertEqual(response.status_code, 404)

	def test_publishing_sets_timestamp(self):
		post = Post.objects.create(
			title="Timestamped",
			slug="timestamped",
			author=self.author,
			content="Article body.",
			status=Post.Status.PUBLISHED,
		)

		self.assertIsNotNone(post.published_at)

	def test_post_content_keeps_formatting_and_removes_unsafe_markup(self):
		post = Post.objects.create(
			title="Formatted",
			slug="formatted",
			author=self.author,
			content='<p>Use <strong>bold</strong>.</p><script>alert("x")</script>',
			status=Post.Status.PUBLISHED,
		)

		response = self.client.get(reverse("posts:detail", args=[post.slug]))

		self.assertContains(response, "<strong>bold</strong>", html=True)
		self.assertNotContains(response, "<script>")
		self.assertNotIn("alert(\"x\")", post.content)

	@override_settings(DEBUG=True, ALLOWED_HOSTS=["testserver"])
	def test_uploaded_cover_image_is_available_on_post_page(self):
		image = SimpleUploadedFile(
			"cover.png",
			(
				b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
				b"\x00\x00\x00\x01\x00\x00\x00\x01"
				b"\x08\x02\x00\x00\x00\x90wS\xde"
				b"\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\xcf\xc0"
				b"\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
				b"\x00\x00\x00\x00IEND\xaeB`\x82"
			),
			content_type="image/png",
		)
		post = Post.objects.create(
			title="Cover image article",
			slug="cover-image-article",
			author=self.author,
			content="Article body.",
			cover_image=image,
			status=Post.Status.PUBLISHED,
		)

		try:
			self.assertTrue(post.cover_image.storage.exists(post.cover_image.name))
			response = self.client.get(reverse("posts:detail", args=[post.slug]))

			self.assertContains(
				response,
				f'<img class="post-cover" src="{post.cover_image.url}"',
				html=False,
			)
		finally:
			post.cover_image.delete(save=False)
from django.test import TestCase

# Create your tests here.
