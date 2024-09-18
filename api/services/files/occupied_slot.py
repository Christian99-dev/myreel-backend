from api.sessions.files import BaseFileSessionManager

def create(occupied_slot_id: int, file_extension: str, file: bytes, file_session: BaseFileSessionManager) -> str:
    """Erstellt eine neue Datei im angegebenen Verzeichnis."""
    return file_session.create(str(occupied_slot_id), file_extension, file, "occupied_slots")

def get(occupied_slot_id: int, file_session: BaseFileSessionManager) -> bytes:
    """Holt die Datei basierend auf der occupied_slot_id (ohne Erweiterung)."""
    return file_session.get(str(occupied_slot_id), "occupied_slots")

def update(occupied_slot_id: int, file: bytes, file_session: BaseFileSessionManager) -> str:
    """Aktualisiert eine vorhandene Datei basierend auf der occupied_slot_id (ohne Erweiterung)."""
    return file_session.update(str(occupied_slot_id), file, "occupied_slots")

def remove(occupied_slot_id: int, file_session: BaseFileSessionManager) -> None:
    """Löscht eine vorhandene Datei basierend auf der occupied_slot_id (ohne Erweiterung)."""
    file_session.remove(str(occupied_slot_id), "occupied_slots")
