class BaseProcessor:
    def source(self, file):
        raise NotImplementedError()

    def save(self, file, format: str):
        raise NotImplementedError()
