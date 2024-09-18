from api.sessions.files import BaseFileSessionManager

def create(edit_id: int, file_extension: str, file: bytes, file_session: BaseFileSessionManager) -> str:
    """Erstellt eine neue Datei im angegebenen Verzeichnis."""
    return file_session.create(str(edit_id), file_extension, file, "edits")

def get(edit_id: int, file_session: BaseFileSessionManager) -> bytes:
    """Holt die Datei basierend auf der edit_id (ohne Erweiterung)."""
    return file_session.get(str(edit_id), "edits")

def update(edit_id: int, file: bytes, file_session: BaseFileSessionManager) -> str:
    """Aktualisiert eine vorhandene Datei basierend auf der edit_id (ohne Erweiterung)."""
    return file_session.update(str(edit_id), file, "edits")

def remove(edit_id: int, file_session: BaseFileSessionManager) -> None:
    """Löscht eine vorhandene Datei basierend auf der edit_id (ohne Erweiterung)."""
    file_session.remove(str(edit_id), "edits")
