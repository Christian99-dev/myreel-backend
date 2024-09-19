import pytest

from api.exceptions.sessions.instagram import InstagramUploadError
from api.services.instagram.upload import upload
from api.sessions.instagram import MemoryInstagramSessionManager


def test_upload_success(memory_instagram_session: MemoryInstagramSessionManager):
    """Testet den erfolgreichen Upload eines Videos über die upload()-Funktion."""
    # Arrange
    video_bytes = b"test_video_data"
    video_format = "mp4"
    caption = "Test Caption"

    # Act & Assert
    try:
        upload(video_bytes, video_format, caption, memory_instagram_session)
    except InstagramUploadError:
        pytest.fail("InstagramUploadError should not be raised for valid inputs")

def test_upload_missing_caption(memory_instagram_session: MemoryInstagramSessionManager):
    """Testet den Fehlerfall, wenn der Titel (caption) in der upload()-Funktion fehlt."""
    # Arrange
    video_bytes = b"test_video_data"
    video_format = "mp4"
    caption = ""  # Leerer Titel

    # Act & Assert
    with pytest.raises(InstagramUploadError, match="Video bytes or caption are missing."):
        upload(video_bytes, video_format, caption, memory_instagram_session)
