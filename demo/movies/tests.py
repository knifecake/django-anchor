from django.core.files.base import ContentFile
from django.test import TestCase

from movies.models import Movie


class MovieTestCase(TestCase):
    def test_attach_cover(self):
        movie = Movie.objects.create(title="Test Movie")
        movie.cover = ContentFile(b"test", name="test.txt")
        self.assertIsNotNone(movie.cover)
