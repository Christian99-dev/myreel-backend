from api.sessions.files import BaseFileSessionManager

def create(song_id: int, file_extension: str, file: bytes, file_session: BaseFileSessionManager) -> str:
    """Erstellt eine neue Datei im angegebenen Verzeichnis."""
    return file_session.create(str(song_id), file_extension, file, "songs")

def get(song_id: int, file_session: BaseFileSessionManager) -> bytes:
    """Holt die Datei basierend auf der song_id (ohne Erweiterung)."""
    return file_session.get(str(song_id), "songs")

def update(song_id: int, file: bytes, file_session: BaseFileSessionManager) -> str:
    """Aktualisiert eine vorhandene Datei basierend auf der song_id (ohne Erweiterung)."""
    return file_session.update(str(song_id), file, "songs")

def remove(song_id: int, file_session: BaseFileSessionManager) -> None:
    """Löscht eine vorhandene Datei basierend auf der song_id (ohne Erweiterung)."""
    file_session.remove(str(song_id), "songs")
