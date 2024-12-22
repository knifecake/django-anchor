from django.core.files.base import ContentFile
from django.test import TestCase

from movies.models import Movie


class MovieTestCase(TestCase):
    def test_attach_cover(self):
        movie = Movie.objects.create(title="Test Movie")
        movie.cover = ContentFile(b"test", name="test.txt")
        self.assertIsNotNone(movie.cover)


class TestPrefetching(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie = Movie.objects.create(title="Test Movie")
        cls.movie.cover = ContentFile(b"test", name="test.txt")
        cls.movie.save()

    def test_prefetch_cover_with_single_object(self):
        movie = Movie.objects.prefetch_related("cover").get(id=self.movie.id)
        with self.assertNumQueries(0):
            self.assertEqual(movie.cover.filename, "test.txt")

    def test_prefetch_cover_with_multiple_objects(self):
        movies = [Movie.objects.create(title="Test Movie %d" % i) for i in range(10)]
        for movie in movies:
            movie.cover = ContentFile(b"test", name="test.txt")
            movie.save()

        movies = list(Movie.objects.prefetch_related("cover").all())
        with self.assertNumQueries(0):
            for movie in movies:
                self.assertEqual(movie.cover.filename, "test.txt")
