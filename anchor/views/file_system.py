from django.core.files.storage import storages
from django.core.signing import BadSignature
from django.http import Http404
from django.http.response import FileResponse
from django.views import View

from anchor.models import Blob


class FileSystemView(View):
    def get(self, request, signed_key, filename=None):
        try:
            key = Blob.unsign_id(signed_key)
            service = storages.create_storage(storages.backends[key["backend"]])
            response = FileResponse(
                service.open(key["key"]),
                content_type=key["content_type"],
                as_attachment=False,
                filename=filename,
            )
            return response
        except (FileNotFoundError, BadSignature, KeyError):
            raise Http404("Not Found")
