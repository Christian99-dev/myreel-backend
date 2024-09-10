from api.sessions.files import BaseFileSessionManager

def get(occupied_slot_id: int, media_access: BaseFileSessionManager) -> bytes:
    """Holt sich eine Mediendatei basierend auf der slot_id."""
    files = media_access.list("occupied_slots")
    
    for file_name in files:
        if file_name.startswith(f"{occupied_slot_id}."):
            media_data = media_access.get(file_name, "occupied_slots")
            return media_data
    return None

def create(occupied_slot_id: int, file_extension: str, file: bytes, media_access: BaseFileSessionManager) -> str:
    """Speichert eine neue Mediendatei basierend auf der slot_id und der Dateierweiterung."""
    file_name = f"{occupied_slot_id}.{file_extension}"  # z.B. "1.slot"
    location = media_access.save(file_name, "occupied_slots", file)
    
    if not location:
        raise Exception("Fehler beim Speichern der Datei.")
    
    return location

def remove(occupied_slot_id: int, media_access: BaseFileSessionManager) -> bool:
    """Entfernt eine Mediendatei basierend auf der slot_id."""
    file_extension = None
    files = media_access.list("occupied_slots")
    
    for file in files:
        if file.startswith(f"{occupied_slot_id}."):
            file_extension = file.split('.')[-1]
            break

    if file_extension:
        media_access.delete("occupied_slots", f"{occupied_slot_id}.{file_extension}")
        return True
    return False

def update(occupied_slot_id: int, file_extension: str, file: bytes, media_access: BaseFileSessionManager) -> str:
    """Aktualisiert eine bestehende Mediendatei, indem die alte gelöscht und eine neue hinzugefügt wird."""
    remove(occupied_slot_id, media_access)  # Alte Datei entfernen
    return create(occupied_slot_id, file_extension, file, media_access)  # Neue Datei hinzufügen
