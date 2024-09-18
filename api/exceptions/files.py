class FileSessionError(Exception):
    """Allgemeiner Fehler für Dateisitzungen."""
    pass

class FileNotFoundInSessionError(FileSessionError):
    """Wird ausgelöst, wenn eine Datei nicht gefunden wird."""
    pass

class FileExistsInSessionError(FileSessionError):
    """Wird ausgelöst, wenn eine Datei bereits existiert."""
    pass

class DirectoryNotFoundError(FileSessionError):
    """Wird ausgelöst, wenn ein Verzeichnis nicht gefunden wird."""
    pass

class FileUpdateError(FileSessionError):
    """Wird ausgelöst, wenn eine Datei nicht aktualisiert werden kann."""
    pass

class FileDeleteError(FileSessionError):
    """Wird ausgelöst, wenn eine Datei nicht gelöscht werden kann."""
    pass
