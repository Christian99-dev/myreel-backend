from api.sessions.files import BaseFileSessionManager

def get(song_id: int, media_access: BaseFileSessionManager) -> bytes:
    """Holt sich eine Mediendatei basierend auf der cover_id."""
    files = media_access.list("covers")
    
    for file_name in files:
        if file_name.startswith(f"{song_id}."):
            media_data = media_access.get(file_name, "covers")
            return media_data
    return None

def create(song_id: int, file_extension: str, file: bytes, media_access: BaseFileSessionManager) -> str:
    """Speichert eine neue Mediendatei basierend auf der cover_id und der Dateierweiterung."""
    file_name = f"{song_id}.{file_extension}"  # z.B. "123.cover"
    location = media_access.save(file_name, "covers", file)
    
    if not location:
        raise Exception("Fehler beim Speichern der Datei.")
    
    return location

def remove(song_id: int, media_access: BaseFileSessionManager) -> bool:
    """Entfernt eine Mediendatei basierend auf der cover_id."""
    file_extension = None
    files = media_access.list("covers")
    
    for file in files:
        if file.startswith(f"{song_id}."):
            file_extension = file.split('.')[-1]
            break

    if file_extension:
        media_access.delete("covers", f"{song_id}.{file_extension}")
        return True
    return False

def update(song_id: int, file_extension: str, file: bytes, media_access: BaseFileSessionManager) -> str:
    """Aktualisiert eine bestehende Mediendatei, indem die alte gelöscht und eine neue hinzugefügt wird."""
    remove(song_id, media_access)  # Alte Datei entfernen
    return create(song_id, file_extension, file, media_access)  # Neue Datei hinzufügen
