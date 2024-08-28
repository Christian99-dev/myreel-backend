import datetime
import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
import os
import requests


LOCAL_INSTAGRAM_ACCESS = bool(strtobool(os.getenv("LOCAL_INSTAGRAM_ACCESS")))

class BaseInstagramAccess(ABC):
    @abstractmethod
    def upload(self, video_bytes: str, caption: str) -> bool:
        pass

class RemoteInstagramAcccess(BaseInstagramAccess):
    def upload(self, video_bytes: str, caption: str) -> bool:
        print("instagram.upload() remote")
        return
        
class LocalInstagramAcccess(BaseInstagramAccess):
    def __init__(self):
        self.instagram_repo = os.getenv("LOCAL_INSTAGRAM_REPO")
        
        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.instagram_repo):
            os.makedirs(self.instagram_repo)

    def upload(self, video_bytes: bytes, caption: str) -> bool:
        try:
            # Generiere einen Dateinamen mit Zeitstempel
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            filepath = os.path.join(self.instagram_repo, filename)

            # Schreibe das Video in eine Datei
            with open(filepath, 'wb') as video_file:
                video_file.write(video_bytes)
            
            # Speichere die Bildunterschrift in einer separaten Datei
            caption_filename = f"caption_{timestamp}.txt"
            caption_filepath = os.path.join(self.instagram_repo, caption_filename)

            with open(caption_filepath, 'w') as caption_file:
                caption_file.write(caption)
            
            print(f"Video successfully saved to {filepath} with caption.")
            return True
        except Exception as e:
            print(f"Failed to save video locally: {e}")
            return False
    
class MemoryInstagramAcccess(BaseInstagramAccess):
    def upload(self, video_bytes: str, caption: str):
        print("instagram.upload() memory")
        pass

instagram_access = LocalInstagramAcccess() if LOCAL_INSTAGRAM_ACCESS else RemoteInstagramAcccess()
