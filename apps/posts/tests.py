from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import clean_rich_text


class EditorImageUploadTests(TestCase):
	def make_png(self):
		image_data = BytesIO()
		Image.new("RGB", (2, 2), color="red").save(image_data, format="PNG")
		return SimpleUploadedFile(
			"pasted.png",
			image_data.getvalue(),
			content_type="image/png",
		)

	def test_staff_can_upload_image_for_rich_text(self):
		staff_user = get_user_model().objects.create_user(
			username="editor",
			password="test-password",
			is_staff=True,
		)
		self.client.force_login(staff_user)
		with tempfile.TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				response = self.client.post(
					reverse("posts:editor_image_upload"),
					{"image": self.make_png()},
				)

				self.assertEqual(response.status_code, 200)
				image_url = response.json()["url"]
				self.assertIn("/media/editor_images/", image_url)
				self.assertIn(
					image_url,
					clean_rich_text(f'<p><img src="{image_url}" alt=""></p>'),
				)

	def test_non_staff_cannot_upload_image(self):
		user = get_user_model().objects.create_user(
			username="reader",
			password="test-password",
		)
		self.client.force_login(user)

		response = self.client.post(
			reverse("posts:editor_image_upload"),
			{"image": self.make_png()},
		)

		self.assertEqual(response.status_code, 302)

	def test_invalid_image_is_rejected(self):
		staff_user = get_user_model().objects.create_user(
			username="editor",
			password="test-password",
			is_staff=True,
		)
		self.client.force_login(staff_user)

		response = self.client.post(
			reverse("posts:editor_image_upload"),
			{
				"image": SimpleUploadedFile(
					"not-an-image.png",
					b"not an image",
					content_type="image/png",
				)
			},
		)

		self.assertEqual(response.status_code, 400)
