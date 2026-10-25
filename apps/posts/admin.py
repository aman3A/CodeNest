from django.contrib import admin

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("name",)}
	search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "category", "status", "published_at")
	list_filter = ("status", "category", "created_at")
	search_fields = ("title", "content", "excerpt")
	prepopulated_fields = {"slug": ("title",)}
	date_hierarchy = "created_at"

	class Media:
		css = {"all": ("css/rich-text-editor.css",)}
		js = ("js/rich-text-editor.js",)
from django.contrib import admin

# Register your models here.
