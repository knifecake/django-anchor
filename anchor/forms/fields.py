from django import forms

from .widgets import ClearableBlobInput


class BlobField(forms.FileField):
    widget = ClearableBlobInput
