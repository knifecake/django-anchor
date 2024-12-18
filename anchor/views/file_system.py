from django.core.signing import BadSignature
from django.http import Http404
from django.http.response import FileResponse
from django.views import View

from anchor.models import Blob


class BlobFileSystemView(View):
    def get(self, request, signed_key, filename=None):
        blob = self.get_blob(signed_key)
        try:
            response = FileResponse(
                blob.open(mode="rb"),
                content_type=blob.mime_type,
                as_attachment=False,
            )
            return response
        except FileNotFoundError:
            raise Http404("Not Found")

    def get_blob(self, signed_key):
        try:
            key = Blob._get_signer().unsign(signed_key)
            return Blob.objects.get(key=key)
        except (Blob.DoesNotExist, BadSignature):
            raise Http404("Not Found")
