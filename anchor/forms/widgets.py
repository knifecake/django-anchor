from django.forms.widgets import ClearableFileInput


class SingleAttachmentInput(ClearableFileInput):
    # make this widget work with the Django admin
    choices = []


class AdminSingleAttachmentInput(SingleAttachmentInput):
    template_name = "anchor/widgets/admin_blob_input.html"
