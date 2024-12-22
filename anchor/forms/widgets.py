from django.forms.widgets import ClearableFileInput


class ClearableBlobInput(ClearableFileInput):
    # make this widget work with the Django admin
    choices = []


class AdminBlobInput(ClearableBlobInput):
    template_name = "anchor/widgets/admin_blob_input.html"
