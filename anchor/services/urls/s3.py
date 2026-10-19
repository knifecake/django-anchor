import os
from threading import Lock
from weakref import WeakKeyDictionary

from django.utils import timezone

from anchor.services.urls.base import BaseURLGenerator

_clients = WeakKeyDictionary()
_clients_lock = Lock()


def _reset_clients():
    # Clients and locks inherited from another process must never be reused.
    global _clients, _clients_lock
    _clients = WeakKeyDictionary()
    _clients_lock = Lock()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_reset_clients)


def _signing_client(storage):
    # Only the low-level client is shared. Sessions/resources are not thread-safe.
    # Key by storage identity so aliases and replacement settings stay isolated.
    with _clients_lock:
        clients = _clients.setdefault(storage, {})
        signed = storage.querystring_auth
        if signed not in clients:
            # Optional S3 dependencies are only needed when this generator is used.
            from botocore import UNSIGNED
            from botocore.config import Config

            config = storage.client_config
            if not signed:
                config = config.merge(Config(signature_version=UNSIGNED))
            session = storage._create_session()
            clients[signed] = session.client(
                "s3",
                region_name=storage.region_name,
                use_ssl=storage.use_ssl,
                endpoint_url=storage.endpoint_url,
                config=config,
                verify=storage.verify,
            )
        return clients[signed]


class S3URLGenerator(BaseURLGenerator):
    """
    URL Generator for use with the S3Backend from the ``django-storages``
    package. Reuses a process-local signing client across request threads.
    """

    def url(
        self,
        key: str,
        expires_in: timezone.timedelta = None,
        filename: str = None,
        mime_type: str = None,
        disposition: str = None,
    ) -> str:
        expire = int(expires_in.total_seconds()) if expires_in is not None else None
        parameters = {}
        if mime_type:
            parameters["ResponseContentType"] = mime_type
        if disposition:
            disposition_value = disposition
            if filename:
                disposition_value = f'{disposition}; filename="{filename}"'
            parameters["ResponseContentDisposition"] = disposition_value

        storage = self.storage
        if storage.custom_domain:
            # Preserve django-storages' custom-domain and CloudFront behavior.
            return storage.url(key, expire=expire, parameters=parameters)

        from storages.utils import clean_name

        parameters["Bucket"] = storage.bucket_name
        parameters["Key"] = storage._normalize_name(clean_name(key))
        if expire is None:
            expire = storage.querystring_expire
        return _signing_client(storage).generate_presigned_url(
            "get_object", Params=parameters, ExpiresIn=expire, HttpMethod=None
        )
