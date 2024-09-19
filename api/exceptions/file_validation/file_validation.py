class InvalidFileTypeException(Exception):
    def __init__(self, message="Ungültiger Dateityp angegeben."):
        self.message = message
        super().__init__(self.message)

class InvalidFileFormatException(Exception):
    def __init__(self, message="Ungültiges Dateiformat."):
        self.message = message
        super().__init__(self.message)

class FileTooLargeException(Exception):
    def __init__(self, max_size_mb):
        self.message = f"Datei ist zu groß. Maximal erlaubt: {max_size_mb} MB."
        super().__init__(self.message)