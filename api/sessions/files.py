import copy
import logging
import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
from typing import Dict, Generator, List, Optional

from dotenv import load_dotenv

from api.exceptions.sessions.files import DirectoryNotFoundError, FileDeleteError, FileExistsInSessionError, FileNotFoundInSessionError

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

    def _fill(self, input_dir: str) -> None:
        """Füllt den Dateispeicher mit Dateien aus einem Verzeichnis."""
        logger.info(f"_fill()")
        self._clear()  # Zuerst den Inhalt löschen
        for root, _, files in os.walk(input_dir):
            relative_path = os.path.relpath(root, input_dir)
            for file_name in files:
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rb') as f:
                    file_data = f.read()

                    # Dateiname und Erweiterung trennen
                    file_name_without_extension, file_extension = os.path.splitext(file_name)
                    file_extension = file_extension.lstrip('.')  # Entfernt den Punkt (.)

                    try:
                        self.create(file_name_without_extension, file_extension, file_data, relative_path)
                    except FileExistsInSessionError:
                        logger.warning(f"File '{file_name}' in '{relative_path}' already exists.")


    def _print(self) -> None:
        """Druckt alle Dateien im Dateispeicher."""
        logger.info(f"_print()")
        all_files = self.list_all()
        logger.info(f"All files in file storage: {all_files}")

    def _clear(self) -> None:
        """Löscht alle Dateien und Verzeichnisse im Dateispeicher."""
        logger.info(f"_clear()")
        self.clear()

    @abstractmethod
    def create(self, file_name: str, file_extension: str, file_data: bytes, dir: str) -> str:
        """Speichert eine Datei."""
        pass

    @abstractmethod
    def get(self, file_name: str, dir: str) -> bytes:
        """Liest eine Datei."""
        pass

    @abstractmethod
    def update(self, file_name: str, file_data: bytes, dir: str) -> str:
        """Aktualisiert eine Datei."""
        pass

    @abstractmethod
    def remove(self, file_name: str, dir: str) -> None:
        """Löscht eine Datei."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Löscht alle Dateien und Verzeichnisse."""
        pass

    @abstractmethod
    def list(self, dir: str) -> List[str]:
        """Listet alle Dateien in einem Verzeichnis auf."""
        pass

    @abstractmethod
    def list_all(self) -> List[str]:
        """Listet alle Dateien im Dateispeicher auf."""
        pass


"""Implementations for Different File Session Managers"""
class LocalFileSessionManager(BaseFileSessionManager):
    def __init__(self) -> None:
        """Initialisiert den lokalen Dateispeicher."""
        logger.info(f"__init__(): (local)")
        self.local_media_repo_folder = f"./outgoing/files"
        os.makedirs(self.local_media_repo_folder, exist_ok=True)
        logger.info(f"__init__(): Local file storage initialized at {self.local_media_repo_folder}")

        if FILES_LOCAL_FILL:
            logger.info(f"__init__(): Filling file storage with mock data")
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

    def create(self, file_name: str, file_extension: str, file_data: bytes, dir: str) -> str:
        """Speichert eine Datei mit Dateinamen und Dateiendung."""
        complete_file_name = f"{file_name}.{file_extension}"
        file_path = os.path.join(self.local_media_repo_folder, dir, complete_file_name)
        
        if os.path.exists(file_path):
            raise FileExistsInSessionError(f"File '{complete_file_name}' already exists in '{dir}'")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"create(): Saved file '{complete_file_name}' in '{dir}'")
        return f"http://localhost:8000/outgoing/files/{dir}/{complete_file_name}"

    def get(self, file_name: str, dir: str) -> bytes:
        """Liest eine Datei basierend auf dem Dateinamen (ohne Endung)."""
        files = self.list(dir)
        for file in files:
            if file.startswith(f"{file_name}."):
                logger.info(f"get(): Retrieved file '{file}' from '{dir}'")
                file_path = os.path.join(self.local_media_repo_folder, dir, file)
                with open(file_path, 'rb') as f:
                    return f.read()
        
        raise FileNotFoundInSessionError(f"File '{file_name}' not found in '{dir}'")

    def update(self, file_name: str, file_data: bytes, dir: str) -> str:
        """Aktualisiert eine Datei basierend auf ihrem Dateinamen (ohne Endung)."""
        files = self.list(dir)
        for file in files:
            if file.startswith(f"{file_name}."):
                file_path = os.path.join(self.local_media_repo_folder, dir, file)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                logger.info(f"update(): Updated file '{file}' in '{dir}'")
                return f"http://localhost:8000/outgoing/files/{dir}/{file}"
        
        raise FileNotFoundInSessionError(f"File '{file_name}' not found in '{dir}'")

    def remove(self, file_name: str, dir: str) -> None:
        """Löscht eine Datei basierend auf ihrem Dateinamen (ohne Endung)."""
        files = self.list(dir)
        for file in files:
            if file.startswith(f"{file_name}."):
                file_path = os.path.join(self.local_media_repo_folder, dir, file)
                os.remove(file_path)
                logger.info(f"remove(): Deleted file '{file}' from '{dir}'")
                return
        
        raise FileDeleteError(f"File '{file_name}' not found in '{dir}'")

    def clear(self) -> None:
        logger.info(f"clear(): Clearing all files from '{self.local_media_repo_folder}'")
        for dirpath, _, filenames in os.walk(self.local_media_repo_folder, topdown=False):
            for filename in filenames:
                os.remove(os.path.join(dirpath, filename))
            for dirname in os.listdir(dirpath):
                os.rmdir(os.path.join(dirpath, dirname))

    def list(self, dir: str) -> List[str]:
        dir_path = os.path.join(self.local_media_repo_folder, dir)
        if not os.path.exists(dir_path):
            raise DirectoryNotFoundError(f"Directory '{dir}' does not exist")
        
        files = os.listdir(dir_path)
        logger.info(f"list(): Listing files in directory '{dir}': {files}")
        return files

    def list_all(self) -> List[str]:
        all_files = []
        for dirpath, _, filenames in os.walk(self.local_media_repo_folder):
            for filename in filenames:
                relative_path = os.path.relpath(os.path.join(dirpath, filename), self.local_media_repo_folder)
                all_files.append(relative_path)
        return all_files

class MemoryFileSessionManager(BaseFileSessionManager):
    def __init__(self) -> None:
        """Initialisiert den Dateispeicher im Speicher und füllt ihn mit Daten."""
        logger.info(f"__init__(): (memory)")
        self.memory_storage: Dict[str, Dict[str, bytes]] = {}
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

    def create(self, file_name: str, file_extension: str, file_data: bytes, dir: str) -> str:
        """Speichert eine Datei mit Dateinamen und Dateiendung im Speicher."""
        complete_file_name = f"{file_name}.{file_extension}"
        if dir not in self.memory_storage:
            self.memory_storage[dir] = {}
        if complete_file_name in self.memory_storage[dir]:
            raise FileExistsInSessionError(f"File '{complete_file_name}' already exists in memory under '{dir}'")
        self.memory_storage[dir][complete_file_name] = file_data
        logger.info(f"create(): Saved file '{complete_file_name}' in memory under '{dir}'")
        return f"memory://{dir}/{complete_file_name}"

    def get(self, file_name: str, dir: str) -> bytes:
        """Liest eine Datei basierend auf dem Dateinamen (ohne Endung) aus dem Speicher."""
        if dir not in self.memory_storage:
            raise DirectoryNotFoundError(f"Directory '{dir}' not found in memory")
        for file in self.memory_storage[dir]:
            if file.startswith(f"{file_name}."):
                logger.info(f"get(): Retrieved file '{file}' from memory under '{dir}'")
                return self.memory_storage[dir][file]
        raise FileNotFoundInSessionError(f"File '{file_name}' not found in memory under '{dir}'")

    def update(self, file_name: str, file_data: bytes, dir: str) -> str:
        """Aktualisiert eine Datei basierend auf ihrem Dateinamen (ohne Endung) im Speicher."""
        if dir not in self.memory_storage:
            raise DirectoryNotFoundError(f"Directory '{dir}' not found in memory")
        for file in self.memory_storage[dir]:
            if file.startswith(f"{file_name}."):
                self.memory_storage[dir][file] = file_data
                logger.info(f"update(): Updated file '{file}' in memory under '{dir}'")
                return f"memory://{dir}/{file}"
        raise FileNotFoundInSessionError(f"File '{file_name}' not found in memory under '{dir}'")

    def remove(self, file_name: str, dir: str) -> None:
        """Löscht eine Datei basierend auf ihrem Dateinamen (ohne Endung) aus dem Speicher."""
        if dir not in self.memory_storage:
            raise DirectoryNotFoundError(f"Directory '{dir}' not found in memory")
        for file in list(self.memory_storage[dir].keys()):
            if file.startswith(f"{file_name}."):
                del self.memory_storage[dir][file]
                logger.info(f"remove(): Deleted file '{file}' from memory under '{dir}'")
                return
        raise FileDeleteError(f"File '{file_name}' not found in memory under '{dir}'")

    def clear(self) -> None:
        logger.info(f"clear(): Clearing all memory storage")
        self.memory_storage.clear()

    def list(self, dir: str) -> List[str]:
        if dir not in self.memory_storage:
            raise DirectoryNotFoundError(f"list(): Directory '{dir}' not found in memory")
        files = list(self.memory_storage.get(dir, {}).keys())
        logger.info(f"list(): Listing files in memory directory '{dir}': {files}")
        return files

    def list_all(self) -> List[str]:
        all_files = [f"{dir}/{file}" for dir, files in self.memory_storage.items() for file in files.keys()]
        return all_files

class RemoteFileSessionManager(BaseFileSessionManager):
    def __init__(self) -> None:
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

    def create(self, file_name: str, file_extension: str, file_data: bytes, dir: str) -> str:
        logger.info(f"save(): Saving file '{file_name}' remotely in '{dir}' (not implemented)")
        return "remote://not-implemented"

    def get(self, file_name: str, dir: str) -> bytes:
        logger.info(f"get(): Retrieving file '{file_name}' remotely from '{dir}' (not implemented)")
        return None

    def update(self, file_name: str, file_data: bytes, dir: str) -> str:
        logger.info(f"update(): Updating file '{file_name}' remotely in '{dir}' (not implemented)")
        return "remote://not-implemented"

    def remove(self, file_name: str, dir: str) -> None:
        logger.info(f"delete(): Deleting file '{file_name}' remotely from '{dir}' (not implemented)")

    def clear(self) -> None:
        logger.info(f"clear(): Clearing all remote files (not implemented)")

    def list(self, dir: str) -> List[str]:
        logger.info(f"list(): Listing files remotely in '{dir}' (not implemented)")
        return []

    def list_all(self) -> List[str]:
        logger.info(f"list_all(): Listing all remote files (not implemented)")
        return []

_file_session_manager = None

def init_file_session_manager() -> None:
    global _file_session_manager
    logger.info(f"init_file_session_manager()")
    
    if _file_session_manager is None:
        _file_session_manager = LocalFileSessionManager() if FILES_LOCAL else RemoteFileSessionManager()
    else:
        logger.warning(f"init_file_session_manager(): already initialized")

def get_file_session() -> Generator[Optional[BaseFileSessionManager], None, None]:
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
