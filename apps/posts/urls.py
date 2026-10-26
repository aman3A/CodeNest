from django.urls import path

from .views import PostDetailView, upload_editor_image

app_name = "posts"

urlpatterns = [
    path("editor-images/upload/", upload_editor_image, name="editor_image_upload"),
    path("<slug:slug>/", PostDetailView.as_view(), name="detail"),
]
