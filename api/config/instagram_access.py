import datetime
import os
from abc import ABC, abstractmethod
from distutils.util import strtobool
import os
import tempfile
import time
import requests
import asyncio
from ftplib import FTP, error_perm


LOCAL_INSTAGRAM_ACCESS = bool(strtobool(os.getenv("LOCAL_INSTAGRAM_ACCESS")))

class BaseInstagramAccess(ABC):
    @abstractmethod
    def upload(self, video_bytes: str, video_format: str, caption: str) -> bool:
        pass

class RemoteInstagramAcccess(BaseInstagramAccess):
    def __init__(self):
        
        # insta
        self.instagram_api_url = os.getenv("INSTAGRAM_API_URL")
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_user_id = os.getenv("INSTAGRAM_USER_ID")
        
        self.ftp_host                   = os.getenv("FTP_HOST")
        self.ftp_user                   = os.getenv("FTP_USER")  
        self.ftp_pass                   = os.getenv("FTP_PASS") 
        self.ftp_repo                   = os.getenv("FTP_REPO") 
        self.ftp_repo_container_link    = os.getenv("FTP_REPO_CONTAINER_LINK") 
        
    def upload(self, video_bytes: str, video_format: str, caption: str) -> bool:
        
        temp_file_path = None
        try:
            # Schritt 1: FTP-Verbindung herstellen
            ftp = FTP(self.ftp_host)
            ftp.login(user=self.ftp_user, passwd=self.ftp_pass)

            # Schritt 2: Überprüfen, ob der Ordner existiert und gegebenenfalls erstellen
            try:
                ftp.cwd(f"public_html/{self.ftp_repo}")  
            except error_perm:
                # Ordner existiert nicht, also erstelle ihn
                ftp.mkd(f"public_html/{self.ftp_repo}")

                # Nach der Erstellung in das Verzeichnis wechseln
                ftp.cwd(f"public_html/{self.ftp_repo}")
                
             
            # Schritt 3: Temporäre Datei erstellen und die Bytes speichern
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{video_format}') as temp_file:
                temp_file.write(video_bytes)
                temp_file_path = temp_file.name
            
            # Schritt 4: Datei auf den FTP-Server hochladen
            remote_file_path_to_save_into = f"{os.path.basename(temp_file_path)}"  # Ordner und Dateiname
            
            with open(temp_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_file_path_to_save_into}', file)

            # public url
            video_url = f"{self.ftp_repo_container_link}/{os.path.basename(temp_file_path)}"
            print(f"Video wurde erfolgreich auf den FTP-Server hochgeladen: {video_url}")
                        

            # # Schritt 5: Erstellen des Video-Containers in Instagram
            create_media_endpoint = f"{self.instagram_api_url}/{self.ig_user_id}/media"
            create_media_data = {
                "video_url": video_url,
                "caption": caption,
                "access_token": self.instagram_access_token,
                "media_type": "REELS"
            }

            create_media_response = requests.post(create_media_endpoint, data=create_media_data)
            create_media_result = create_media_response.json()

            if create_media_response.status_code == 200 and "id" in create_media_result:
                container_id = create_media_result["id"]
                print(f"Media container created with ID: {container_id}")
            else:
                print(f"Failed to create media container: {create_media_result}")
                return False

            # Wartezeit, um sicherzustellen, dass die Media ID verfügbar ist
            time.sleep(100)  # Warte 2 Minuten, nicht blockierend
            
            # Schritt 6: Veröffentlichen des Videos
            publish_media_endpoint = f"{self.instagram_api_url}/{self.ig_user_id}/media_publish"
            publish_media_data = {
                "creation_id": container_id,
                "access_token": self.instagram_access_token,
            }

            publish_media_response = requests.post(publish_media_endpoint, data=publish_media_data)
            publish_media_result = publish_media_response.json()

            if publish_media_response.status_code == 200 and "id" in publish_media_result:
                print(f"Video published successfully with Media ID: {publish_media_result['id']}")
                return True
            else:
                print(f"Failed to publish video: {publish_media_result}")
                return False

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

        finally:
            # Schritt 7: Temporäre Datei löschen und FTP-Verbindung schließen
            if temp_file_path is not None and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            try:
                ftp.quit()
            except Exception as e:
                print(f"Error closing FTP connection: {e}")
        
class LocalInstagramAcccess(BaseInstagramAccess):
    def __init__(self):
        self.instagram_repo = os.getenv("LOCAL_INSTAGRAM_REPO")
        
        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.instagram_repo):
            os.makedirs(self.instagram_repo)

    def upload(self, video_bytes: str, video_format: str, caption: str) -> bool:
        try:
            # Generiere einen Dateinamen mit Zeitstempel
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.{video_format}"
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
    def upload(self, video_bytes: str, video_format: str, caption: str) -> bool:
        print("instagram.upload() memory")
        pass

instagram_access = LocalInstagramAcccess() if LOCAL_INSTAGRAM_ACCESS else RemoteInstagramAcccess()

def get_instagram_access(): 
    return instagram_access
