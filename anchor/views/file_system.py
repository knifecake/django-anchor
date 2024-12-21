from django.core.files.storage import storages
from django.core.signing import BadSignature
from django.http import Http404
from django.http.response import FileResponse
from django.views import View

from anchor.models import Blob
from anchor.settings import anchor_settings


class FileSystemView(View):
    def get(self, request, signed_key, filename=None):
        try:
            key = Blob.unsign_id(signed_key, purpose="file_system")
            service = storages.create_storage(storages.backends[key["backend"]])
            response = FileResponse(
                service.open(key["key"]),
                content_type=key.get("mime_type", anchor_settings.DEFAULT_MIME_TYPE),
                as_attachment=False,
                filename=filename,
            )
            return response
        except (FileNotFoundError, BadSignature, KeyError):
            raise Http404("Not Found")
