import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
import os
import requests


LOCAL_INSTAGRAM_ACCESS = strtobool(os.getenv("LOCAL_INSTAGRAM_ACCESS"))

class BaseInstagramAccess(ABC):
    @abstractmethod
    def upload(self) -> bool:
        pass

class RemoteInstagramAcccess(BaseInstagramAccess):
    def upload(self, video_path: str, caption: str) -> bool:
        
        print("instagram.upload() remote")
        return
        try:
            # Schritt 1: Beginnen Sie mit dem Video-Upload
            create_container_url = f"https://graph.facebook.com/v16.0/{self.instagram_user_id}/media"
            params = {
                "media_type": "VIDEO",
                "video_url": video_path,
                "caption": caption,
                "access_token": self.instagram_access_token
            }
            response = requests.post(create_container_url, params=params)
            response_data = response.json()

            if "id" not in response_data:
                print(f"Fehler beim Erstellen des Medien-Containers: {response_data}")
                return False

            container_id = response_data["id"]

            # Schritt 2: Veröffentlichen Sie das Video
            publish_url = f"https://graph.facebook.com/v16.0/{self.instagram_user_id}/media_publish"
            publish_params = {
                "creation_id": container_id,
                "access_token": self.instagram_access_token
            }
            publish_response = requests.post(publish_url, params=publish_params)
            publish_data = publish_response.json()

            if "id" in publish_data:
                print("Das Video wurde erfolgreich auf Instagram hochgeladen.")
                return True
            else:
                print(f"Fehler beim Veröffentlichen des Videos: {publish_data}")
                return False

        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            return False
    
class LocalInstagramAcccess(BaseInstagramAccess):
    def upload(self):
        print("instagram.upload() local")
        pass
    
class MemoryInstagramAcccess(BaseInstagramAccess):
    def upload(self):
        print("instagram.upload() memory")
        pass

instagram_access = LocalInstagramAcccess() if LOCAL_INSTAGRAM_ACCESS else RemoteInstagramAcccess()
