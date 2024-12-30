class BaseProcessor:
    """
    Interface for file processors.

    A file processor must implement the :py:meth:`source` method and
    :py:meth:`save` methods outlined below at the minimum.

    For convenience, the :py:meth:`source` method returns the processor itself,
    so you can chain methods together. Check out the :py:class:`PillowProcessor
    <anchor.services.processors.pillow.PillowProcessor>` for an example
    implementation.
    """

    def source(self, file):
        """
        Set up the processor to work with the given file.

        The `file` passed is a file-like object that responds to ``read``, like
        a ``DjangoFile`` or an ``io`` stream.
        """
        raise NotImplementedError()

    def save(self, file, format: str):
        """
        Save the processed file to the given file-like object.

        The `file` passed is a file-like object that responds to ``write``, like
        a ``TemporaryFile`` or an ``io`` stream.

        The `format` is a string representing the file format to save the file
        as, like ``'jpeg'`` or ``'png'``.
        """
        raise NotImplementedError()
