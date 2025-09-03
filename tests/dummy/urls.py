from django.urls import path

from tests.dummy.views import DummyListView, DummyUpdateView

app_name = "dummy"

urlpatterns = [
    path("", DummyListView.as_view(), name="list"),
    path("<int:pk>/", DummyUpdateView.as_view(), name="update"),
]
