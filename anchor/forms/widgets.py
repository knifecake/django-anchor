from django.forms.widgets import ClearableFileInput


class ClearableBlobInput(ClearableFileInput):
    """
    Replacement for Django's ClearableFileInput widget that works with
    BlobFields.
    """

    # make this widget work with the Django admin
    choices = []


class AdminBlobInput(ClearableBlobInput):
    template_name = "anchor/widgets/admin_blob_input.html"
