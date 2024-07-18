from huey.contrib.djhuey import task


@task()
def blob_make_variant(blob, variant_name, format_params):
    blob.make_variant(variant_name, format_params)
