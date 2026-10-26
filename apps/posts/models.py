from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import nh3
from taggit.managers import TaggableManager

RICH_TEXT_TAGS = {
	"a", "blockquote", "br", "code", "del", "div", "em", "h2", "h3",
	"h4", "hr", "i", "img", "li", "ol", "p", "pre", "s", "span",
	"strong", "sub", "sup", "u", "ul",
}
RICH_TEXT_ATTRIBUTES = {
	"a": {"href", "title"},
	"img": {"alt", "src", "title"},
}


def clean_rich_text(value):
	return nh3.clean(
		value or "",
		tags=RICH_TEXT_TAGS,
		attributes=RICH_TEXT_ATTRIBUTES,
		url_schemes={"http", "https", "mailto"},
	)


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(max_length=120, unique=True)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "categories"

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Post(models.Model):
	class Status(models.TextChoices):
		DRAFT = "draft", "Draft"
		PUBLISHED = "published", "Published"

	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=220, unique=True)
	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="posts",
	)
	category = models.ForeignKey(
		Category,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="posts",
	)
	excerpt = models.CharField(max_length=300, blank=True)
	content = models.TextField()
	cover_image = models.ImageField(upload_to="post_covers/", blank=True)
	tags = TaggableManager(blank=True)
	status = models.CharField(
		max_length=10,
		choices=Status.choices,
		default=Status.DRAFT,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	published_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-published_at", "-created_at"]

	def save(self, *args, **kwargs):
		self.content = clean_rich_text(self.content)
		if self.status == self.Status.PUBLISHED and self.published_at is None:
			self.published_at = timezone.now()
		elif self.status == self.Status.DRAFT:
			self.published_at = None
		super().save(*args, **kwargs)

	def __str__(self):
		return self.title
from django.db import models

# Create your models here.
