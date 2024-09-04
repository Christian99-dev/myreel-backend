from api.sessions.files import BaseMediaAccess


def get(song_id: int, media_access: BaseMediaAccess) -> bytes:
    """Holt sich eine Mediendatei basierend auf der song_id."""
    # Zuerst die Liste der Dateien im Verzeichnis "songs" abrufen
    files = media_access.list("songs")
    
    # Suche nach einer Datei, die mit der song_id beginnt und die korrekte Erweiterung hat
    for file_name in files:
        if file_name.startswith(str(song_id) + "."):
            # Wenn die Datei gefunden wird, lade sie herunter
            media_data = media_access.get(file_name, "songs")
            return media_data
    return None

def create(song_id: int, file_extension: str, file: bytes, media_access: BaseMediaAccess) -> str:
    """Speichert eine neue Mediendatei basierend auf der song_id und der Dateierweiterung."""
    # Erstelle den Dateinamen aus der song_id und der Dateierweiterung
    file_name = f"{song_id}.{file_extension}"  # z.B. "1234.mp3"
    location = media_access.save(file_name, "songs", file)
    
    if not location:
        raise Exception("Fehler beim Speichern der Datei.")
    
    return location

def remove(song_id: int, media_access: BaseMediaAccess):
    file_extension = None
    # Zuerst überprüfen, ob die Datei existiert und die Erweiterung abrufen
    files = media_access.list("songs")
    for file in files:
        if file.startswith(f"{song_id}."):
            file_extension = file.split('.')[-1]  # Hole die Dateierweiterung
            break

    # Wenn die Datei gefunden wurde, entferne sie
    if file_extension:
        media_access.delete("songs", f"{song_id}.{file_extension}")
        return True  # Rückgabe, dass die Datei erfolgreich entfernt wurde
    return False  # Rückgabe, dass die Datei nicht gefunden wurde