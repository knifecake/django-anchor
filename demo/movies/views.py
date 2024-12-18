from django.views.generic import DetailView, UpdateView

from movies.models import Movie


class MovieDetailView(DetailView):
    model = Movie


class MovieUpdateView(UpdateView):
    model = Movie
    fields = ["title", "cover"]

    def get(self, request, *args, **kwargs):
        # print(Movie._meta.get_field("cover"))
        return super().get(request, *args, **kwargs)