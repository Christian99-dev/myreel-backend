from abc import ABC, abstractmethod
import copy
import os
from typing import Generator
from dotenv import load_dotenv
from distutils.util import strtobool


"""ENV"""
load_dotenv()
FILES_LOCAL      = bool(strtobool(os.getenv("FILES_LOCAL")))
FILES_LOCAL_FILL = bool(strtobool(os.getenv("FILES_LOCAL_FILL")))


"""Base File Session Manager"""
class BaseFileSessionManager(ABC):

    @abstractmethod
    def __init__(self):
        """Initialisiert den Dateispeicher."""
        pass

    @abstractmethod
    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine Dateisitzung."""
        pass

    def _fill(self, input_dir: str):
        """Füllt den Dateispeicher mit Dateien aus einem Verzeichnis."""
        self._clear()  # Zuerst den Inhalt löschen
        for root, _, files in os.walk(input_dir):
            relative_path = os.path.relpath(root, input_dir)
            for file_name in files:
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    self.save(file_name, relative_path, file_data)

    def _print(self):
        """Druckt alle Dateien im Dateispeicher."""
        all_files = self.list_all()
        print(f"All files in file storage: {all_files}")

    def _clear(self):
        """Löscht alle Dateien und Verzeichnisse im Dateispeicher."""
        self.clear()

    """Session specific methods"""
    @abstractmethod
    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        """Speichert eine Datei."""
        pass

    @abstractmethod
    def get(self, file_name: str, dir: str):
        """Liest eine Datei."""
        pass

    @abstractmethod
    def list(self, dir: str):
        """Listet alle Dateien in einem Verzeichnis auf."""
        pass

    @abstractmethod
    def list_all(self):
        """Listet alle Dateien im Dateispeicher auf."""
        pass

    @abstractmethod
    def delete(self, dir: str, file_name: str) -> None:
        """Löscht eine Datei."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Löscht alle Dateien und Verzeichnisse."""
        pass


"""Implementations for Different File Session Managers"""
class LocalFileSessionManager(BaseFileSessionManager):
    def __init__(self):
        """Initialisiert den lokalen Dateispeicher."""
        self.local_media_repo_folder = f"./outgoing/files"
        os.makedirs(self.local_media_repo_folder, exist_ok=True)
        if FILES_LOCAL_FILL:
            self._fill("mock/files")
        self._print()

    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine lokale Dateisitzung."""
        try:
            print(f"Starting local file session for {self.local_media_repo_folder}")
            yield self
        finally:
            print(f"Ending local file session for {self.local_media_repo_folder}")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return f"http://localhost:8000/outgoing/files/{dir}/{file_name}"

    def get(self, file_name: str, dir: str):
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def list(self, dir: str):
        dir_path = os.path.join(self.local_media_repo_folder, dir)
        if os.path.exists(dir_path):
            return os.listdir(dir_path)
        return []

    def list_all(self):
        all_files = []
        for dirpath, _, filenames in os.walk(self.local_media_repo_folder):
            for filename in filenames:
                relative_path = os.path.relpath(os.path.join(dirpath, filename), self.local_media_repo_folder)
                all_files.append(relative_path)
        return all_files

    def delete(self, dir: str, file_name: str) -> None:
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    def clear(self) -> None:
        for dirpath, _, filenames in os.walk(self.local_media_repo_folder, topdown=False):
            for filename in filenames:
                os.remove(os.path.join(dirpath, filename))
            for dirname in os.listdir(dirpath):
                os.rmdir(os.path.join(dirpath, dirname))

class MemoryFileSessionManager(BaseFileSessionManager):
    def __init__(self):
        """Initialisiert den Dateispeicher im Speicher und füllt ihn mit Daten."""
        self.memory_storage = {}
        # Ruft _fill aus der Basisklasse auf, um den Speicher zu füllen
        self._fill("mock/files")

    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine transaktionale Dateisitzung im Speicher."""
        # Kopie des aktuellen Speichers erstellen, um Änderungen rückgängig machen zu können
        session_memory = copy.deepcopy(self.memory_storage)
        try:
            # print("Starting in-memory file session")
            self.memory_storage = session_memory  # Nutze die Kopie während der Sitzung
            yield self  # Gib den Manager zurück, um Zugriff auf die Methoden zu haben
            # Änderungen übernehmen, wenn die Sitzung erfolgreich beendet wurde
        finally:
            # print("Ending in-memory file session (rollback if necessary)")
            pass

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        if dir not in self.memory_storage:
            self.memory_storage[dir] = {}
        self.memory_storage[dir][file_name] = file_data
        return f"memory://{dir}/{file_name}"

    def get(self, file_name: str, dir: str):
        return self.memory_storage.get(dir, {}).get(file_name, None)

    def list(self, dir: str):
        return list(self.memory_storage.get(dir, {}).keys())

    def list_all(self):
        all_files = {dir: list(files.keys()) for dir, files in self.memory_storage.items()}
        return all_files

    def delete(self, dir: str, file_name: str) -> None:
        if dir in self.memory_storage and file_name in self.memory_storage[dir]:
            del self.memory_storage[dir][file_name]

    def clear(self) -> None:
        self.memory_storage.clear()

class RemoteFileSessionManager(BaseFileSessionManager):
    def __init__(self):
        """Initialisiert den Fernspeicher."""
        pass

    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine Dateisitzung im Fernspeicher."""
        try:
            print("Starting remote file session")
            yield self
        finally:
            print("Ending remote file session")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        return "remote://not-implemented"

    def get(self, file_name: str, dir: str):
        return None

    def list(self, dir: str):
        return []

    def list_all(self):
        return []

    def delete(self, dir: str, file_name: str) -> None:
        pass

    def clear(self) -> None:
        pass

_file_session_manager = None

def get_file_session():
    global _file_session_manager
    
    # beim ersten ausführen
    if _file_session_manager is None:
        _file_session_manager = LocalFileSessionManager() if FILES_LOCAL else MemoryFileSessionManager()
    
    # Öffnet die Session und gibt sie zurück
    gen = _file_session_manager.get_session()
    session = next(gen)
    yield session