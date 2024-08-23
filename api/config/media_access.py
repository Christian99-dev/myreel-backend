import os
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from distutils.util import strtobool

import logging
logger = logging.getLogger("testing")

load_dotenv()
LOCAL_MEDIA = strtobool(os.getenv("LOCAL_MEDIA"))

# Base
class MediaAccess(ABC):
    @abstractmethod
    def save(self, file_name: str, file_data: bytes) -> str:
        pass

    @abstractmethod
    def get(self, file_name: str) -> bytes:
        pass

# Versions
class LocalMediaAccess(MediaAccess):
    def __init__(self, base_path: str):
        self.base_path = base_path
        # Sicherstellen, dass der Ordner existiert
        os.makedirs(self.base_path, exist_ok=True)  

    def save(self, file_name: str, file_data: bytes) -> str:
        file_path = os.path.join(self.base_path, file_name)
        with open(file_path, 'wb') as file:
            file.write(file_data)
        return file_path

    def get(self, file_name: str) -> bytes:
        file_path = os.path.join(self.base_path, file_name)
        with open(file_path, 'rb') as file:
            return file.read()

class CloudMediaAccess(MediaAccess):
    def save(self, file_name: str, file_data: bytes) -> str:
        pass

    def get(self, file_name: str) -> bytes:
        pass
    
class InMemoryMediaAccess(MediaAccess):
    def save(self, file_name: str, file_data: bytes) -> str:
        pass

    def get(self, file_name: str) -> bytes:
        pass
    
def get_media_access() -> MediaAccess:
    if LOCAL_MEDIA:
        return LocalMediaAccess(base_path="static")
    else:
        return CloudMediaAccess()

media_dependency = Annotated[MediaAccess, Depends(get_media_access)]