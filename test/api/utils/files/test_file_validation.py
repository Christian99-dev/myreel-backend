from io import BytesIO
from unittest.mock import MagicMock

from fastapi import UploadFile

from api.utils.files.file_validation import file_validation


# Tests für die Datei-Validierung
def test_valid_video_file():
    """Test für eine gültige Videodatei."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "video/mp4"  # Setze den Inhaltstyp
    
    result, message = file_validation(mock_file, "video")
    assert result is not None
    assert message == "Datei erfolgreich validiert."

def test_invalid_file_type():
    """Test für eine Datei mit ungültigem Typ."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "text/plain"  # Ungültiger Typ
    
    result, message = file_validation(mock_file, "video")
    assert result is None
    assert message == "Dateityp text/plain nicht erlaubt für video."

def test_exceeding_file_size():
    """Test für eine Datei, die die maximal erlaubte Größe überschreitet."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_file.mp4"
    mock_file.file = BytesIO(b"x" * ((100 * 1024 * 1024) + 1))  #> 100 MB
    mock_file.content_type = "video/mp4"  # Gültiger Typ
    mock_file.file.seek(0)  # Setze den Datei-Stream zurück
    
    result, message = file_validation(mock_file, "video")
    assert result is None
    assert message == "Datei ist zu groß für video. Maximal erlaubt: 100.0 MB."

def test_sanitizing_file_name():
    """Test für die Sanitizing-Logik des Dateinamens."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test file@name?.mp4"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "video/mp4"  # Gültiger Typ
    
    result, message = file_validation(mock_file, "video")
    assert result is not None
    assert result.filename == "test_file_name_.mp4"
    assert message == "Datei erfolgreich validiert."

def test_invalid_file_type_in_image():
    """Test für eine ungültige Bilddatei."""
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_image.png"
    mock_file.file = BytesIO(b"test content")
    mock_file.content_type = "application/pdf"  # Ungültiger Typ für Bild
    
    result, message = file_validation(mock_file, "image")
    assert result is None
    assert message == "Dateityp application/pdf nicht erlaubt für image."