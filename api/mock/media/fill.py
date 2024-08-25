import os
from api.config.media_access import BaseMediaAccess

def fill(media_access: BaseMediaAccess, source_dir: str = "api/mock/media/model"):
    """Spiegelt die Dateien aus dem Quellverzeichnis in das Zielverzeichnis des media_access."""
    media_access.clear()
    for root, dirs, files in os.walk(source_dir):
        # Berechne das relative Verzeichnis
        relative_path = os.path.relpath(root, source_dir)
        
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as f:
                file_data = f.read()
                # Speichere die Datei im media_access
                media_access.save(file_name, relative_path, file_data)