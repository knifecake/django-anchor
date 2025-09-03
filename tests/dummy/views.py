from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from tests.dummy.models import Dummy


class DummyListView(ListView):
    model = Dummy
    template_name = "dummy/dummy_list.html"


class DummyUpdateView(UpdateView):
    model = Dummy
    template_name = "dummy/dummy_update.html"
    fields = ["name", "cover"]
    success_url = reverse_lazy("dummy:list")
