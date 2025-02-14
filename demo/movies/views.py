from django.views.generic import DetailView, UpdateView

from movies.models import Movie


class MovieDetailView(DetailView):
    def get_queryset(self):
        return Movie.objects.prefetch_related("cover")


class MovieUpdateView(UpdateView):
    model = Movie
    fields = ["title", "cover"]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
