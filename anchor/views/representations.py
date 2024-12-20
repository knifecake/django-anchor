from django.core.signing import BadSignature
from django.http import Http404, HttpResponseRedirect
from django.views import View

from anchor.models import Blob, Variant


class RepresentationView(View):
    def get(self, request, signed_blob_id, variation_key, filename=None):
        representation: Variant = self.get_representation(signed_blob_id, variation_key)
        return HttpResponseRedirect(representation.get_url())

    def get_representation(self, signed_blob_id, variation_key):
        try:
            blob = Blob.objects.get_signed(signed_blob_id)
            return blob.representation(variation_key).processed
        except (Blob.DoesNotExist, BadSignature):
            raise Http404("Not Found")
