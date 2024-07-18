from django import forms

from anchor.models.blob import Blob

from .widgets import ClearableBlobInput


class BlobField(forms.FileField):
    """
    A form field for uploading a file and storing it as a Blob.

    This field is intended to replace the default Django FileField in forms.
    """

    widget = ClearableBlobInput

    def __init__(self, *args, **kwargs):
        # remove ModelChoiceField attributes from kwargs for compatibility
        kwargs.pop("limit_choices_to", None)
        kwargs.pop("queryset", None)
        kwargs.pop("to_field_name", None)
        kwargs.pop("blank", None)
        return super().__init__(*args, **kwargs)

    def prepare_value(self, value: str):
        if value:
            try:
                blob = Blob.objects.get(pk=value)
                return blob.file
            except Blob.DoesNotExist:
                return None
        return value

    def clean(self, data, initial=None):
        if isinstance(initial, Blob):
            initial_file = initial.file
        elif isinstance(initial, str):
            initial_blob = Blob.objects.filter(pk=initial).first()
            if initial_blob:
                initial_file = initial_blob.file
            else:
                initial_file = None
        else:
            initial_file = None

        file = super().clean(data, initial=initial_file)

        if file is False:
            return None
        elif file is None:
            if initial is not None:
                return Blob.objects.get(pk=initial)
            else:
                return None
        else:
            blob = Blob.from_file(file)
            blob.save()
            return blob
