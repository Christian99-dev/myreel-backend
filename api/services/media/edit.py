from api.config.media_access import BaseMediaAccess

def get(edit_id: int, media_access: BaseMediaAccess) -> bytes:
    """Holt sich eine Mediendatei basierend auf der edit_id."""
    files = media_access.list("edits")
    
    for file_name in files:
        if file_name.startswith(f"{edit_id}."):
            media_data = media_access.get(file_name, "edits")
            return media_data
    return None

def create(edit_id: int, file_extension: str, file: bytes, media_access: BaseMediaAccess) -> str:
    """Speichert eine neue Mediendatei basierend auf der edit_id und der Dateierweiterung."""
    file_name = f"{edit_id}.{file_extension}"  # z.B. "5678.mp3"
    location = media_access.save(file_name, "edits", file)
    
    if not location:
        raise Exception("Fehler beim Speichern der Datei.")
    
    return location

def remove(edit_id: int, media_access: BaseMediaAccess) -> bool:
    """Entfernt eine Mediendatei basierend auf der edit_id."""
    file_extension = None
    files = media_access.list("edits")
    
    for file in files:
        if file.startswith(f"{edit_id}."):
            file_extension = file.split('.')[-1]
            break

    if file_extension:
        media_access.delete("edits", f"{edit_id}.{file_extension}")
        return True
    return False

def update(edit_id: int, file_extension: str, file: bytes, media_access: BaseMediaAccess) -> str:
    """Aktualisiert eine bestehende Mediendatei, indem die alte gelöscht und eine neue hinzugefügt wird."""
    remove(edit_id, media_access)  # Alte Datei entfernen
    return create(edit_id, file_extension, file, media_access)  # Neue Datei hinzufügen
