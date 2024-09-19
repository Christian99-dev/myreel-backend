from io import BytesIO
from unittest.mock import MagicMock

import pytest
from fastapi import UploadFile

from api.utils.files.file_validation import (FileTooLargeException,
                                             InvalidFileFormatException,
                                             InvalidFileTypeException,
                                             file_validation)

# Tests für die Datei-Validierung mit pytest.raises

def test_valid_video_file():
    """Test für eine gültige Videodatei."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "video/mp4"  # Setze den Inhaltstyp

    result = file_validation(mock_file, "video")
    assert result is not None  # Erfolgreiche Validierung

def test_invalid_file_type_exception():
    """Test für ungültigen Dateityp, der eine InvalidFileTypeException auslösen sollte."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "video/mp4"  # Gültiger Typ

    with pytest.raises(InvalidFileTypeException, match="Ungültiger Dateityp angegeben."):
        file_validation(mock_file, "invalid_type")

def test_invalid_file_format_exception():
    """Test für eine Datei mit ungültigem Format, das eine InvalidFileFormatException auslösen sollte."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "text/plain"  # Ungültiges Format für Video

    with pytest.raises(InvalidFileFormatException, match="Dateityp text/plain nicht erlaubt für video."):
        file_validation(mock_file, "video")

def test_exceeding_file_size_exception():
    """Test für eine Datei, die die maximal erlaubte Größe überschreitet und eine FileTooLargeException auslösen sollte."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"x" * ((100 * 1024 * 1024) + 1))  # > 100 MB
    mock_file.content_type = "video/mp4"  # Gültiger Typ
    mock_file.file.seek(0)  # Setze den Datei-Stream zurück

    with pytest.raises(FileTooLargeException, match="Datei ist zu groß. Maximal erlaubt: 100.0 MB."):
        file_validation(mock_file, "video")

def test_sanitizing_file_name():
    """Test für die Sanitizing-Logik des Dateinamens."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test file@name?.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "video/mp4"  # Gültiger Typ

    result = file_validation(mock_file, "video")
    assert result is not None
    assert result.filename == "test_file_name_.mp4"  # Überprüfen, ob der Dateiname richtig sanitisiert wurde

