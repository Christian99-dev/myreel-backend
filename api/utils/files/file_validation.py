
import re
from typing import Optional, Tuple

from fastapi import UploadFile

from api.config.file import file_config


def file_validation(file: UploadFile, file_type: str) -> Tuple[Optional[UploadFile], str]:
    """Validiere die Datei basierend auf dem Typ und gebe die sanitierte Datei zurück oder None sowie eine Nachricht."""
    # Überprüfe, ob der Dateityp gültig ist
    if file_type not in file_config:
        return None, "Ungültiger Dateityp angegeben."

    allowed_formats = file_config[file_type]["formats"]
    max_size = file_config[file_type]["max_size"]

    # Überprüfe das Dateiformat
    if file.content_type not in allowed_formats:
        return None, f"Dateityp {file.content_type} nicht erlaubt für {file_type}."

    # Überprüfe die Dateigröße
    file_size = len(file.file.read())
    if file_size > max_size:
        return None, f"Datei ist zu groß für {file_type}. Maximal erlaubt: {max_size / (1024 * 1024)} MB."

    # Setze den Datei-Stream zurück
    file.file.seek(0)

    # Sanitizing des Dateinamens
    sanitized_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
    file.filename = sanitized_name  # Setze den neuen Dateinamen
    
    return file, "Datei erfolgreich validiert."