from django import forms

from .widgets import SingleAttachmentInput


class SingleAttachmentField(forms.FileField):
    widget = SingleAttachmentInput
