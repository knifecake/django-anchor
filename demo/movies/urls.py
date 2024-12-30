from django.urls import path

from movies import views

app_name = "movies"

urlpatterns = [
    path("movies/<int:pk>/", views.MovieDetailView.as_view(), name="movie_detail"),
    path(
        "movies/<int:pk>/update/", views.MovieUpdateView.as_view(), name="movie_update"
    ),
]
