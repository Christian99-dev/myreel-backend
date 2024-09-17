import copy
import logging
import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
from typing import Generator

from dotenv import load_dotenv

# Logger für die Session-Verwaltung
logger = logging.getLogger("sessions.files")

"""ENV"""
load_dotenv()
FILES_LOCAL = bool(strtobool(os.getenv("FILES_LOCAL")))
FILES_LOCAL_FILL = bool(strtobool(os.getenv("FILES_LOCAL_FILL")))
FILES_PRINT = bool(strtobool(os.getenv("FILES_PRINT")))

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
        logger.info(f"_fill()")
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
        logger.info(f"_print()")
        all_files = self.list_all()
        logger.info(f"All files in file storage: {all_files}")

    def _clear(self):
        """Löscht alle Dateien und Verzeichnisse im Dateispeicher."""
        logger.info(f"_clear()")
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
        logger.info(f"__init__(): (local)")
        self.local_media_repo_folder = f"./outgoing/files"
        os.makedirs(self.local_media_repo_folder, exist_ok=True)
        logger.info(f"__init__(): Local file storage initialized at {self.local_media_repo_folder}")

        if FILES_LOCAL_FILL:
            logger.info(f"__init__(): Filling file storage with mock data")
        
        if FILES_LOCAL_FILL:
            self._fill("mock/files")
            
        if FILES_PRINT:
            self._print()

    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine lokale Dateisitzung."""
        logger.info(f"get_session(): (local)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (local)")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        logger.info(f"save(): Saved file '{file_name}' in '{dir}'")
        return f"http://localhost:8000/outgoing/files/{dir}/{file_name}"

    def get(self, file_name: str, dir: str):
        file_path = os.path.join(self.local_media_repo_folder, dir, file_name)
        try:
            with open(file_path, 'rb') as f:
                logger.info(f"get(): Retrieved file '{file_name}' from '{dir}'")
                return f.read()
        except FileNotFoundError:
            logger.error(f"get(): File '{file_name}' not found in '{dir}'")
            return None

    def list(self, dir: str):
        dir_path = os.path.join(self.local_media_repo_folder, dir)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            logger.info(f"list(): Listing files in directory '{dir}': {files}")
            return files
        logger.info(f"list(): Directory '{dir}' does not exist")
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
            logger.info(f"delete(): Deleted file '{file_name}' from '{dir}'")
        except FileNotFoundError:
            logger.error(f"delete(): File '{file_name}' not found in '{dir}'")

    def clear(self) -> None:
        logger.info(f"clear(): Clearing all files from '{self.local_media_repo_folder}'")
        for dirpath, _, filenames in os.walk(self.local_media_repo_folder, topdown=False):
            for filename in filenames:
                os.remove(os.path.join(dirpath, filename))
            for dirname in os.listdir(dirpath):
                os.rmdir(os.path.join(dirpath, dirname))


class MemoryFileSessionManager(BaseFileSessionManager):
    def __init__(self):
        """Initialisiert den Dateispeicher im Speicher und füllt ihn mit Daten."""
        logger.info(f"__init__(): (memory)")
        self.memory_storage = {}
        # Ruft _fill aus der Basisklasse auf, um den Speicher zu füllen
        self._fill("mock/files")

    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine transaktionale Dateisitzung im Speicher."""
        logger.info(f"get_session(): (memory)")
        session_memory = copy.deepcopy(self.memory_storage)
        try:
            self.memory_storage = session_memory  # Nutze die Kopie während der Sitzung
            yield self
        finally:
            logger.info(f"get_session(): closed session (memory)")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        if dir not in self.memory_storage:
            self.memory_storage[dir] = {}
        self.memory_storage[dir][file_name] = file_data
        logger.info(f"save(): Saved file '{file_name}' in memory under '{dir}'")
        return f"memory://{dir}/{file_name}"

    def get(self, file_name: str, dir: str):
        logger.info(f"get(): Retrieving file '{file_name}' from memory under '{dir}'")
        return self.memory_storage.get(dir, {}).get(file_name, None)

    def list(self, dir: str):
        files = list(self.memory_storage.get(dir, {}).keys())
        logger.info(f"list(): Listing files in memory directory '{dir}': {files}")
        return files

    def list_all(self):
        all_files = {dir: list(files.keys()) for dir, files in self.memory_storage.items()}
        return all_files

    def delete(self, dir: str, file_name: str) -> None:
        if dir in self.memory_storage and file_name in self.memory_storage[dir]:
            del self.memory_storage[dir][file_name]
            logger.info(f"delete(): Deleted file '{file_name}' from memory under '{dir}'")

    def clear(self) -> None:
        logger.info(f"clear(): Clearing all memory storage")
        self.memory_storage.clear()


class RemoteFileSessionManager(BaseFileSessionManager):
    def __init__(self):
        """Initialisiert den Fernspeicher."""
        logger.info(f"__init__(): (remote)")
        
        if FILES_PRINT:
            self._print()

    def get_session(self) -> Generator["BaseFileSessionManager", None, None]:
        """Erzeugt eine Dateisitzung im Fernspeicher."""
        logger.info(f"get_session(): (remote)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (remote)")

    def save(self, file_name: str, dir: str, file_data: bytes) -> str:
        logger.info(f"save(): Saving file '{file_name}' remotely in '{dir}' (not implemented)")
        return "remote://not-implemented"

    def get(self, file_name: str, dir: str):
        logger.info(f"get(): Retrieving file '{file_name}' remotely from '{dir}' (not implemented)")
        return None

    def list(self, dir: str):
        logger.info(f"list(): Listing files remotely in '{dir}' (not implemented)")
        return []

    def list_all(self):
        logger.info(f"list_all(): Listing all remote files (not implemented)")
        return []

    def delete(self, dir: str, file_name: str) -> None:
        logger.info(f"delete(): Deleting file '{file_name}' remotely from '{dir}' (not implemented)")

    def clear(self) -> None:
        logger.info(f"clear(): Clearing all remote files (not implemented)")


_file_session_manager = None

def init_file_session_manager():
    global _file_session_manager
    logger.info(f"init_file_session_manager()")
    
    if _file_session_manager is None:
        _file_session_manager = LocalFileSessionManager() if FILES_LOCAL else RemoteFileSessionManager()
    else:
        logger.warning(f"init_file_session_manager(): already initialized")


def get_file_session():
    global _file_session_manager
    logger.info(f"get_file_session()")
    
    if _file_session_manager is None:
        logger.error(f"get_file_session(): failed! manager not initialized")
        return

    try:
        gen = _file_session_manager.get_session()
        session = next(gen)
        yield session
    except Exception as e:
        logger.error(f"get_file_session(): Error: {e}")
        raise e
