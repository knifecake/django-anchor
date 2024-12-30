from django.urls import path

from anchor import views

app_name = "anchor"

urlpatterns = [
    path(
        "blobs/redirect/<str:signed_id>/",
        views.blobs.BlobRedirectView.as_view(),
        name="blob_redirect",
    ),
    path(
        "blobs/<str:signed_id>/",
        views.blobs.BlobRedirectView.as_view(),
        name="blob",
    ),
    path(
        "blobs/<str:signed_id>/<str:filename>",
        views.blobs.BlobRedirectView.as_view(),
        name="blob",
    ),
    path(
        "representations/<str:signed_blob_id>/<str:variation_key>/",
        views.representations.RepresentationView.as_view(),
        name="representation",
    ),
    path(
        "representations/<str:signed_blob_id>/<str:variation_key>/<str:filename>",
        views.representations.RepresentationView.as_view(),
        name="representation",
    ),
    path(
        "file-system/<str:signed_key>/",
        views.file_system.FileSystemView.as_view(),
        name="file_system",
    ),
    path(
        "file-system/<str:signed_key>/<str:filename>",
        views.file_system.FileSystemView.as_view(),
        name="file_system",
    ),
]
