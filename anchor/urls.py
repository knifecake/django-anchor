from django.urls import path

from anchor import views

app_name = "anchor"

urlpatterns = [
    path(
        "blobs/redirect/<str:signed_id>/",
        views.blobs.BlobRedirectView.as_view(),
        name="blob_redirect",
    ),
    path("blobs/<str:signed_id>/", views.blobs.BlobRedirectView.as_view(), name="blob"),
    path(
        "disk/<str:signed_key>/",
        views.file_system.BlobFileSystemView.as_view(),
        name="disk",
    ),
]
