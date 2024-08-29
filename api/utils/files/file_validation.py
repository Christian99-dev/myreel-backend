import os
import re
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, Any, Optional, Tuple

# Konfiguration für erlaubte Formate und Größen
CONFIG = {
    "video": {
        "formats": ["video/mp4", "video/x-msvideo", "video/x-matroska"],  # z.B. MP4, AVI, MKV
        "max_size": 100 * 1024 * 1024  # 5 MB in Bytes
    },
    "image": {
        "formats": ["image/jpeg", "image/png", "image/gif"],  # z.B. JPEG, PNG, GIF
        "max_size": 10 * 1024 * 1024  # 2 MB in Bytes
    },
    "audio": {
        "formats": ["audio/mpeg", "audio/wav"],  # z.B. MP3, WAV
        "max_size": 10 * 1024 * 1024  # 10 MB in Bytes
    }
}

def file_validation(file: UploadFile, file_type: str) -> Tuple[Optional[UploadFile], str]:
    """Validiere die Datei basierend auf dem Typ und gebe die sanitierte Datei zurück oder None sowie eine Nachricht."""
    # Überprüfe, ob der Dateityp gültig ist
    if file_type not in CONFIG:
        return None, "Ungültiger Dateityp angegeben."

    allowed_formats = CONFIG[file_type]["formats"]
    max_size = CONFIG[file_type]["max_size"]

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