from django.utils import timezone

from anchor.services.urls.base import BaseURLGenerator


class S3URLGenerator(BaseURLGenerator):
    """
    URL Generator for use with the S3Backend from the ``django-storages``
    package.
    """

    def url(
        self,
        key: str,
        expires_in: timezone.timedelta = None,
        filename: str = None,
        mime_type: str = None,
        disposition: str = None,
    ) -> str:
        expire = expires_in.total_seconds() if expires_in else None
        parameters = {}
        if mime_type:
            parameters["ResponseContentType"] = mime_type
        if disposition:
            parameters["ResponseContentDisposition"] = disposition
        return self.storage.url(key, expire=expire, parameters=parameters)
