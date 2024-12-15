from django.views import View
from django.http.response import HttpResponseRedirect
from anchor.models import Blob
from django.core.signing import BadSignature
from django.http import Http404


class BlobRedirectView(View):
    def get(self, request, signed_id):
        blob = self.get_blob(signed_id)
        return HttpResponseRedirect(blob.url)

    def get_blob(self, signed_id):
        try:
            return Blob.objects.get_signed(signed_id)
        except (Blob.DoesNotExist, BadSignature):
            raise Http404("Not Found")