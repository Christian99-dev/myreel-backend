from distutils.util import strtobool
import os
import logging
from abc import ABC, abstractmethod

from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("testing")

load_dotenv()
LOCAL_MEDIA_ACCESS = strtobool(os.getenv("LOCAL_MEDIA_ACCESS"))

class BaseMediaAccess(ABC):
    def __init__(self):
        self.setup()  # Ruft die Setup-Methode der spezifischen Klasse auf

    @abstractmethod
    def save(self, file_name: str, dir: str, file_data: bytes) -> None:
        pass

    @abstractmethod
    def get(self, file_name: str, dir: str):
        pass

    @abstractmethod
    def setup(self):
        """Methode zur Initialisierung, die in den Unterklassen implementiert wird."""
        pass


class LocalMediaAccess(BaseMediaAccess):
    def setup(self):
        """Initialisiere lokale Ressourcen."""
        self.static_dir = "./static"
        os.makedirs(self.static_dir, exist_ok=True)  # Erstelle den Ordner, falls nicht vorhanden
        logger.info(f"Local media access setup complete. Directory: {self.static_dir}")

    def save(self, file_name: str, dir: str, file_data: bytes) -> None:
        file_path = os.path.join(self.static_dir, dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        logger.info(f"File saved to {file_path}")

    def get(self, file_name: str, dir: str):
        file_path = os.path.join(self.static_dir, dir, file_name)
        try:
            with open(file_path, 'rb') as f:
                logger.info(f"File retrieved from {file_path}")
                return f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None


class MemoryMediaAccess(BaseMediaAccess):
    def setup(self):
        """Initialisiere Ressourcen für den Speicherzugriff."""
        self.memory_storage = {}
        logger.info("Memory media access setup complete.")

    def save(self, file_name: str, dir: str, file_data: bytes) -> None:
        if dir not in self.memory_storage:
            self.memory_storage[dir] = {}
        self.memory_storage[dir][file_name] = file_data
        logger.info(f"File '{file_name}' saved in memory under directory '{dir}'.")

    def get(self, file_name: str, dir: str):
        return self.memory_storage.get(dir, {}).get(file_name, None)


class RemoteMediaAccess(BaseMediaAccess):
    def setup(self):
        """Initialisiere Ressourcen für den Fernzugriff."""
        logger.info("Remote media access setup complete.")
        # Hier könnte die Verbindung zu einem Remote-Speicher hergestellt werden

    def save(self, file_name: str, dir: str, file_data: bytes) -> None:
        logger.warning("Remote saving not implemented.")

    def get(self, file_name: str, dir: str):
        logger.warning("Remote retrieval not implemented.")


def get_media_access(access_type: str) -> BaseMediaAccess:
    if access_type == "local":
        return LocalMediaAccess()
    elif access_type == "memory":
        return MemoryMediaAccess()
    elif access_type == "remote":
        return RemoteMediaAccess()
    else:
        raise ValueError(f"Invalid access type: {access_type}")


# Beispiel für die Erstellung einer Media Access-Instanz
# media_access = get_media_access("local" if LOCAL_MEDIA_ACCESS else "remote") 
