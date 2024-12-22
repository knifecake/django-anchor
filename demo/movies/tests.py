from unittest import skip

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

    @skip("Not implemented yet")
    def test_prefetch_cover(self):
        movie = Movie.objects.prefetch_related("cover").get(id=self.movie.id)
        with self.assertNumQueries(0):
            self.assertEqual(movie.cover.byte_size, 4)
