import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from anchor.models import Blob
from tests.dummy.models import Dummy


class TestDummyViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dummies = [Dummy.objects.create(name=f"Test {i}") for i in range(10)]
        for dummy in cls.dummies:
            dummy.cover = Blob.objects.from_path(
                os.path.join(settings.BASE_DIR, "fixtures", "garlic.png")
            )

    def test_get_dummy_list_view(self):
        response = self.client.get(reverse("dummy:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dummy/dummy_list.html")

        self.assertRegex(response.content.decode(), r'src="[^"]+"')

    def test_get_dummy_update_view(self):
        dummy = self.dummies[0]
        response = self.client.get(reverse("dummy:update", kwargs={"pk": dummy.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dummy/dummy_update.html")
        self.assertContains(response, dummy.name)
        self.assertRegex(response.content.decode(), 'type="file"')

    def test_post_dummy_update_view_with_a_file(self):
        dummy = self.dummies[0]
        url = reverse("dummy:update", kwargs={"pk": dummy.pk})

        with open(os.path.join(settings.BASE_DIR, "fixtures", "onions.jpg"), "rb") as f:
            response = self.client.post(
                url,
                {
                    "name": "Changed",
                    "cover": f,
                },
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dummy:list"))

        dummy.refresh_from_db()
        self.assertEqual(dummy.name, "Changed")
        self.assertIsNotNone(dummy.cover)
        self.assertEqual(dummy.cover.filename, "onions.jpg")

    def test_post_dummy_update_without_a_file(self):
        dummy = self.dummies[0]
        original_cover = dummy.cover
        url = reverse("dummy:update", kwargs={"pk": dummy.pk})

        response = self.client.post(
            url,
            {
                "name": "Changed",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dummy:list"))

        dummy.refresh_from_db()
        self.assertEqual(dummy.name, "Changed")
        self.assertEqual(dummy.cover, original_cover)
