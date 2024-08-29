import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from distutils.util import strtobool

load_dotenv()
LOCAL_MEDIA_ACCESS = bool(strtobool(os.getenv("LOCAL_MEDIA_ACCESS")))
LOCAL_MEDIA_REPO = os.getenv("LOCAL_MEDIA_REPO")

class BaseMediaAccess(ABC):
    def __init__(self):
        self.setup()  # Ruft die Setup-Methode der spezifischen Klasse auf

    @abstractmethod
    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        """Speichert die Datei und gibt den Speicherort zurück."""
        pass

    @abstractmethod
    def get(self, file_name: str, dir: str):
        pass

    @abstractmethod
    def setup(self):
        """Methode zur Initialisierung, die in den Unterklassen implementiert wird."""
        pass

    @abstractmethod
    def list(self, dir: str):
        """Listet alle Dateien in einem angegebenen Verzeichnis auf."""
        pass

    @abstractmethod
    def list_all(self):
        """Listet alle Dateien im gesamten Medienzugriff auf."""
        pass

    @abstractmethod
    def delete(self, dir: str, file_name: str) -> None:
        """Löscht eine Datei im angegebenen Verzeichnis."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Löscht alle Dateien und Verzeichnisse."""
        pass

class LocalMediaAccess(BaseMediaAccess):
    def setup(self):
        """Initialisiere lokale Ressourcen."""
        self.local_media_repo_folder = f"./{LOCAL_MEDIA_REPO}"
        os.makedirs(self.local_media_repo_folder, exist_ok=True)  # Erstelle den Ordner, falls nicht vorhanden
        # print(f"Local media access setup complete. Directory: {self.static_dir}")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        location = f"http://localhost:8000/{LOCAL_MEDIA_REPO}/{dir}/{file_name}"  # Beispiel für lokale URL
        # print(f"File saved to {file_path}")
        return location

    def get(self, file_name: str, dir: str):
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        try:
            with open(file_path, 'rb') as f:
                # print(f"File retrieved from {file_path}")
                return f.read()
        except FileNotFoundError:
            # print(f"File not found: {file_path}")
            return None

    def list(self, dir: str):
        dir_path = os.path.join(self.local_media_repo_folder, dir)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            # print(f"Files in '{dir}': {files}")
            return files
        else:
            # print(f"Directory not found: {dir_path}")
            return []

    def list_all(self):
        all_files = []
        for dirpath, _, filenames in os.walk(self.local_media_repo_folder):
            for filename in filenames:
                relative_path = os.path.relpath(os.path.join(dirpath, filename), self.local_media_repo_folder)
                all_files.append(relative_path)
        # print("All files in media access:", all_files)
        return all_files

    def delete(self, dir: str, file_name: str) -> None:
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        try:
            os.remove(file_path)
            # print(f"File deleted: {file_path}")
        except FileNotFoundError:
            # print(f"File not found for deletion: {file_path}")
            pass

    def clear(self) -> None:
        """Löscht alle Dateien und Verzeichnisse im lokalen Zugriff, behält jedoch das Hauptverzeichnis."""
        try:
            for dirpath, dirnames, filenames in os.walk(self.local_media_repo_folder, topdown=False):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    os.remove(file_path)
                    # print(f"File cleared: {file_path}")
                for dirname in dirnames:
                    dir_path = os.path.join(dirpath, dirname)
                    os.rmdir(dir_path)
                    # print(f"Directory cleared: {dir_path}")

            # Hier wird nur das Hauptverzeichnis nicht gelöscht.
            # print(f"Cleared all files and directories under: {self.static_dir}")
        except Exception as e:
            # print(f"Error clearing files: {e}")
            pass

class MemoryMediaAccess(BaseMediaAccess):
    def setup(self):
        """Initialisiere Ressourcen für den Speicherzugriff."""
        self.memory_storage = {}
        # print("Memory media access setup complete.")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        if dir not in self.memory_storage:
            self.memory_storage[dir] = {}
        self.memory_storage[dir][file_name] = file_data
        # print(f"File '{file_name}' saved in memory under directory '{dir}'.")
        return f"memory://{dir}/{file_name}"  # Beispiel für Speicherort

    def get(self, file_name: str, dir: str):
        return self.memory_storage.get(dir, {}).get(file_name, None)

    def list(self, dir: str):
        if dir in self.memory_storage:
            files = list(self.memory_storage[dir].keys())
            # print(f"Files in memory under '{dir}': {files}")
            return files
        else:
            # print(f"Directory not found in memory: {dir}")
            return []

    def list_all(self):
        all_files = {dir: list(files.keys()) for dir, files in self.memory_storage.items()}
        # print("All files in memory access:", all_files)
        return all_files

    def delete(self, dir: str, file_name: str) -> None:
        if dir in self.memory_storage and file_name in self.memory_storage[dir]:
            del self.memory_storage[dir][file_name]
            # print(f"File '{file_name}' deleted from memory under directory '{dir}'.")
        else:
            # print(f"File not found for deletion in memory: {dir}/{file_name}")
            pass

    def clear(self) -> None:
        """Löscht alle Dateien und Verzeichnisse im Speicherzugriff."""
        self.memory_storage.clear()
        # print("All files cleared from memory access.")

class RemoteMediaAccess(BaseMediaAccess):
    def setup(self):
        """Initialisiere Ressourcen für den Fernzugriff."""
        # print("Remote media access setup complete.")
        # Hier könnte die Verbindung zu einem Remote-Speicher hergestellt werden

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        # print("Remote saving not implemented.")
        return "remote://not-implemented"  # Platzhalter-Rückgabe

    def get(self, file_name: str, dir: str):
        pass
        # print("Remote retrieval not implemented.")

    def list(self, dir: str):
        # print("Remote listing not implemented.")
        return []

    def list_all(self):
        # print("Remote listing all files not implemented.")
        return []

    def delete(self, dir: str, file_name: str) -> None:
        pass
        # print("Remote deletion not implemented.")

    def clear(self) -> None:
        pass
        # print("Remote clearing not implemented.")

def create_media_access(access_type: str) -> BaseMediaAccess:
    # print("create_media_access()")
    if access_type == "local":
        return LocalMediaAccess()
    elif access_type == "memory":
        return MemoryMediaAccess()
    elif access_type == "remote":
        return RemoteMediaAccess()
    else:
        raise ValueError(f"Invalid access type: {access_type}")

media_access = create_media_access("local" if LOCAL_MEDIA_ACCESS else "remote")

def get_media_access(): 
    return media_access