import os
import time
import datetime
from typing import Generator
import requests
import tempfile
from abc import ABC, abstractmethod
from distutils.util import strtobool
from ftplib import FTP, error_perm

"""ENV"""
LOCAL_INSTAGRAM_ACCESS = bool(strtobool(os.getenv("LOCAL_INSTAGRAM_ACCESS")))

"""Base Instagram Session Manager"""
class BaseInstagramSessionManager(ABC):

    @abstractmethod
    def __init__(self):
        """Initialisiert den Instagram-Zugang."""
        pass

    @abstractmethod
    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine Instagram-Sitzung."""
        pass

    """Session specific methods"""
    @abstractmethod
    def upload(self, video_bytes: bytes, video_format: str, caption: str) -> bool:
        """Lädt ein Video zu Instagram hoch."""
        pass


"""Implementations for Different Instagram Session Managers"""
class RemoteInstagramSessionManager(BaseInstagramSessionManager):
    def __init__(self):
        """Initialisiert den Fernzugriff auf Instagram."""
        # Instagram API
        self.instagram_api_url = os.getenv("INSTAGRAM_API_URL")
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_user_id = os.getenv("INSTAGRAM_USER_ID")

        # FTP
        self.ftp_host = os.getenv("FTP_HOST")
        self.ftp_user = os.getenv("FTP_USER")
        self.ftp_pass = os.getenv("FTP_PASS")
        self.ftp_repo = os.getenv("FTP_REPO")
        self.ftp_repo_container_link = os.getenv("FTP_REPO_CONTAINER_LINK")

    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine Fern-Instagram-Sitzung."""
        try:
            print("Starting remote Instagram session")
            yield self
        finally:
            print("Ending remote Instagram session")

    def upload(self, video_bytes: bytes, video_format: str, caption: str) -> bool:
        """Lädt ein Video über FTP zu Instagram hoch."""
        temp_file_path = None
        try:
            # Schritt 1: FTP-Verbindung herstellen
            ftp = FTP(self.ftp_host)
            ftp.login(user=self.ftp_user, passwd=self.ftp_pass)

            # Schritt 2: Verzeichnis erstellen oder wechseln
            try:
                ftp.cwd(f"public_html/{self.ftp_repo}")
            except error_perm:
                ftp.mkd(f"public_html/{self.ftp_repo}")
                ftp.cwd(f"public_html/{self.ftp_repo}")

            # Schritt 3: Temporäre Datei erstellen und auf FTP hochladen
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{video_format}') as temp_file:
                temp_file.write(video_bytes)
                temp_file_path = temp_file.name

            remote_file_path = f"{os.path.basename(temp_file_path)}"
            with open(temp_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_file_path}', file)

            video_url = f"{self.ftp_repo_container_link}/{remote_file_path}"
            print(f"Video successfully uploaded to FTP: {video_url}")

            # Schritt 5: Instagram-Container erstellen
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

            # Schritt 6: Video veröffentlichen
            time.sleep(100)  # Warte 2 Minuten
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
            if temp_file_path is not None and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            try:
                ftp.quit()
            except Exception as e:
                print(f"Error closing FTP connection: {e}")

class LocalInstagramSessionManager(BaseInstagramSessionManager):
    def __init__(self):
        """Initialisiert den lokalen Instagram-Zugang."""
        self.instagram_repo = os.getenv("LOCAL_INSTAGRAM_REPO")

        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.instagram_repo):
            os.makedirs(self.instagram_repo)

    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine lokale Instagram-Sitzung."""
        try:
            print(f"Starting local Instagram session for {self.instagram_repo}")
            yield self
        finally:
            print(f"Ending local Instagram session for {self.instagram_repo}")

    def upload(self, video_bytes: bytes, video_format: str, caption: str) -> bool:
        """Speichert das Video lokal."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.{video_format}"
            filepath = os.path.join(self.instagram_repo, filename)

            with open(filepath, 'wb') as video_file:
                video_file.write(video_bytes)

            caption_filepath = os.path.join(self.instagram_repo, f"caption_{timestamp}.txt")
            with open(caption_filepath, 'w') as caption_file:
                caption_file.write(caption)

            print(f"Video successfully saved to {filepath} with caption.")
            return True
        except Exception as e:
            print(f"Failed to save video locally: {e}")
            return False

class MemoryInstagramSessionManager(BaseInstagramSessionManager):
    def __init__(self):
        """Initialisiert den E-Mail-Speicher im Speicher."""
        pass

    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine transaktionale Instagram-Sitzung im Speicher."""
        try:
            # print("Starting in-memory Instagram session")
            yield self
        finally:
            pass
            # print("Ending in-memory Instagram session")

    def upload(self, video_bytes: bytes, video_format: str, caption: str) -> bool:
        """Simuliert das Hochladen eines Videos im Speicher."""
        # print(f"Simulating video upload with caption: {caption}")
        return True


_instagram_session_manager = None

def get_instagram_session():
    global _instagram_session_manager

    # beim ersten Ausführen
    if _instagram_session_manager is None:
        _instagram_session_manager = LocalInstagramSessionManager() if LOCAL_INSTAGRAM_ACCESS else RemoteInstagramSessionManager()

    # Öffnet die Session und gibt sie zurück
    gen = _instagram_session_manager.get_session()
    session = next(gen)
    yield session
