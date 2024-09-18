import pytest

from api.exceptions.instagram import InstagramUploadError
from api.sessions.instagram import MemoryInstagramSessionManager


def test_upload_success(memory_instagram_session: MemoryInstagramSessionManager):
    """Testet den erfolgreichen Upload eines Videos."""
    # Arrange
    video_bytes = b"test_video_data"
    video_format = "mp4"
    caption = "Test Caption"

    # Act & Assert
    try:
        memory_instagram_session.upload(video_bytes, video_format, caption)
    except InstagramUploadError:
        pytest.fail("InstagramUploadError should not be raised for valid inputs")

def test_upload_missing_video_bytes(memory_instagram_session: MemoryInstagramSessionManager):
    """Testet den Fehlerfall, wenn video_bytes fehlen."""
    # Arrange
    video_bytes = b""  # Leere Videodaten
    video_format = "mp4"
    caption = "Test Caption"

    # Act & Assert
    with pytest.raises(InstagramUploadError, match="Video bytes or caption are missing."):
        memory_instagram_session.upload(video_bytes, video_format, caption)

def test_upload_missing_caption(memory_instagram_session: MemoryInstagramSessionManager):
    """Testet den Fehlerfall, wenn der Titel (caption) fehlt."""
    # Arrange
    video_bytes = b"test_video_data"
    video_format = "mp4"
    caption = ""  # Leerer Titel

    # Act & Assert
    with pytest.raises(InstagramUploadError, match="Video bytes or caption are missing."):
        memory_instagram_session.upload(video_bytes, video_format, caption)

def test_upload_unsupported_video_format(memory_instagram_session: MemoryInstagramSessionManager):
    """Testet den Fehlerfall für ein nicht unterstütztes Videoformat."""
    # Arrange
    video_bytes = b"test_video_data"
    video_format = "avi"  # Nicht unterstütztes Format
    caption = "Test Caption"

    # Act & Assert
    with pytest.raises(InstagramUploadError, match="Unsupported video format: avi"):
        memory_instagram_session.upload(video_bytes, video_format, caption)
