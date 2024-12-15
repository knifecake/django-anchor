import base64
from typing import Any, Type

from django.core.signing import BadSignature, JSONSerializer, Signer
from django.utils import timezone


class ExpiredSignature(BadSignature):
    pass


class InvalidPurpose(BadSignature):
    pass


class Serializer(JSONSerializer):
    def dumps(self, value: Any) -> str:
        return base64.urlsafe_b64encode(super().dumps(value)).decode()

    def loads(self, value: str) -> Any:
        return super().loads(base64.urlsafe_b64decode(value))


class AnchorSigner(Signer):
    EXPIRES_AT_KEY = "e"
    PURPOSE_KEY = "p"
    VALUE_KEY = "v"

    def __init__(self, *args, serializer: Type[Any] = Serializer, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializer()

    def sign(
        self,
        value: str,
        expires_in: timezone.timedelta = None,
        expires_at: timezone.datetime = None,
        purpose: str = None,
    ) -> str:
        return super().sign(
            self.serializer.dumps(
                self.prepare_value(value, expires_in, expires_at, purpose)
            )
        )

    def unsign(
        self,
        signed_value: str,
        purpose: str = None,
    ) -> str:
        try:
            from_signature = self.serializer.loads(super().unsign(signed_value))
        except BadSignature:
            raise

        if purpose and from_signature.get(self.PURPOSE_KEY) != purpose:
            raise InvalidPurpose("Purpose mismatch")

        if (
            from_signature.get(self.EXPIRES_AT_KEY)
            and from_signature.get(self.EXPIRES_AT_KEY) < timezone.now().timestamp()
        ):
            raise ExpiredSignature("Signature expired")

        return from_signature[self.VALUE_KEY]

    def prepare_value(
        self,
        value: Any,
        expires_in: timezone.timedelta = None,
        expires_at: timezone.datetime = None,
        purpose: str = None,
    ) -> dict[str, Any]:
        to_sign = {}
        if expires_in:
            expires_at = timezone.now() + expires_in

        if expires_at:
            to_sign[self.EXPIRES_AT_KEY] = int(expires_at.timestamp())
        if purpose:
            to_sign[self.PURPOSE_KEY] = purpose
        to_sign[self.VALUE_KEY] = value
        return to_sign
