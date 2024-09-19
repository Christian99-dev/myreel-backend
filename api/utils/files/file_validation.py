
import re

from fastapi import UploadFile

from api.config.file import file_config
from api.exceptions.file_validation.file_validation import (
    FileTooLargeException, InvalidFileFormatException,
    InvalidFileTypeException)


def file_validation(file: UploadFile, file_type: str) -> UploadFile:
    """Validiert die Datei basierend auf dem Typ und gibt die Datei zurück, wenn sie gültig ist. Wirft sonst Ausnahmen."""
    
    # Überprüfe, ob der Dateityp gültig ist
    if file_type not in file_config:
        raise InvalidFileTypeException()

    allowed_formats = file_config[file_type]["formats"]
    max_size = file_config[file_type]["max_size"]

    # Überprüfe das Dateiformat
    if file.content_type not in allowed_formats:
        raise InvalidFileFormatException(f"Dateityp {file.content_type} nicht erlaubt für {file_type}.")

    # Überprüfe die Dateigröße
    file_size = len(file.file.read())
    if file_size > max_size:
        raise FileTooLargeException(max_size / (1024 * 1024))

    # Setze den Datei-Stream zurück
    file.file.seek(0)

    # Sanitizing des Dateinamens
    sanitized_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
    file.filename = sanitized_name  # Setze den neuen Dateinamen

    return file