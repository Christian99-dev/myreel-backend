import datetime
import logging
import os
import tempfile
import time
from abc import ABC, abstractmethod
from distutils.util import strtobool
from ftplib import FTP, error_perm
from typing import Generator

import requests

# Logger für die Session-Verwaltung
logger = logging.getLogger("sessions.instagram")

"""ENV"""
INSTAGRAM_LOCAL = bool(strtobool(os.getenv("INSTAGRAM_LOCAL")))

INSTAGRAM_REMOTE_API_URL = os.getenv("INSTAGRAM_REMOTE_API_URL")
INSTAGRAM_REMOTE_ACCESS_TOKEN = os.getenv("INSTAGRAM_REMOTE_ACCESS_TOKEN")
INSTAGRAM_REMOTE_USER_ID = os.getenv("INSTAGRAM_REMOTE_USER_ID")

INSTAGRAM_REMOTE_FTP_HOST = os.getenv("INSTAGRAM_REMOTE_FTP_HOST")
INSTAGRAM_REMOTE_FTP_USER = os.getenv("INSTAGRAM_REMOTE_FTP_USER")
INSTAGRAM_REMOTE_FTP_PASS = os.getenv("INSTAGRAM_REMOTE_FTP_PASS")
INSTAGRAM_REMOTE_FTP_REPO = os.getenv("INSTAGRAM_REMOTE_FTP_REPO")
INSTAGRAM_REMOTE_FTP_REPO_CONTAINER_LINK = os.getenv("INSTAGRAM_REMOTE_FTP_REPO_CONTAINER_LINK")


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
        logger.info(f"__init__(): (remote)")

    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine Fern-Instagram-Sitzung."""
        logger.info(f"get_session(): (remote)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (remote)")

    def upload(self, video_bytes: bytes, video_format: str, caption: str) -> bool:
        """Lädt ein Video über FTP zu Instagram hoch."""
        temp_file_path = None
        try:
            # Schritt 1: FTP-Verbindung herstellen
            ftp = FTP(INSTAGRAM_REMOTE_FTP_HOST)
            ftp.login(user=INSTAGRAM_REMOTE_FTP_USER, passwd=INSTAGRAM_REMOTE_FTP_PASS)
            logger.info(f"upload(): Connected to FTP server")

            # Schritt 2: Verzeichnis erstellen oder wechseln
            try:
                ftp.cwd(f"public_html/{INSTAGRAM_REMOTE_FTP_REPO}")
            except error_perm:
                ftp.mkd(f"public_html/{INSTAGRAM_REMOTE_FTP_REPO}")
                ftp.cwd(f"public_html/{INSTAGRAM_REMOTE_FTP_REPO}")
            logger.info(f"upload(): Changed to FTP directory: public_html/{INSTAGRAM_REMOTE_FTP_REPO}")

            # Schritt 3: Temporäre Datei erstellen und auf FTP hochladen
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{video_format}') as temp_file:
                temp_file.write(video_bytes)
                temp_file_path = temp_file.name

            remote_file_path = f"{os.path.basename(temp_file_path)}"
            with open(temp_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_file_path}', file)

            video_url = f"{INSTAGRAM_REMOTE_FTP_REPO_CONTAINER_LINK}/{remote_file_path}"
            logger.info(f"upload(): Video successfully uploaded to FTP: {video_url}")

            # Schritt 5: Instagram-Container erstellen
            create_media_endpoint = f"{INSTAGRAM_REMOTE_API_URL}/{INSTAGRAM_REMOTE_USER_ID}/media"
            create_media_data = {
                "video_url": video_url,
                "caption": caption,
                "access_token": INSTAGRAM_REMOTE_ACCESS_TOKEN,
                "media_type": "REELS"
            }
            create_media_response = requests.post(create_media_endpoint, data=create_media_data)
            create_media_result = create_media_response.json()

            if create_media_response.status_code == 200 and "id" in create_media_result:
                container_id = create_media_result["id"]
                logger.info(f"upload(): Media container created with ID: {container_id}")
            else:
                logger.error(f"upload(): Failed to create media container: {create_media_result}")
                return False

            # Schritt 6: Video veröffentlichen
            time.sleep(100)  # Warte 2 Minuten
            publish_media_endpoint = f"{INSTAGRAM_REMOTE_API_URL}/{INSTAGRAM_REMOTE_USER_ID}/media_publish"
            publish_media_data = {
                "creation_id": container_id,
                "access_token": INSTAGRAM_REMOTE_ACCESS_TOKEN,
            }
            publish_media_response = requests.post(publish_media_endpoint, data=publish_media_data)
            publish_media_result = publish_media_response.json()

            if publish_media_response.status_code == 200 and "id" in publish_media_result:
                logger.info(f"upload(): Video published successfully with Media ID: {publish_media_result['id']}")
                return True
            else:
                logger.error(f"upload(): Failed to publish video: {publish_media_result}")
                return False

        except Exception as e:
            logger.error(f"upload(): An error occurred: {e}")
            return False

        finally:
            if temp_file_path is not None and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            try:
                ftp.quit()
                logger.info(f"upload(): FTP connection closed")
            except Exception as e:
                logger.error(f"upload(): Error closing FTP connection: {e}")


class LocalInstagramSessionManager(BaseInstagramSessionManager):
    def __init__(self):
        """Initialisiert den lokalen Instagram-Zugang."""
        logger.info(f"__init__(): (local)")
        self.instagram_repo = "outgoing/instagram"

        # Sicherstellen, dass der Ordner existiert
        if not os.path.exists(self.instagram_repo):
            os.makedirs(self.instagram_repo)
            logger.info(f"__init__(): Created local directory at {self.instagram_repo}")

    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine lokale Instagram-Sitzung."""
        logger.info(f"get_session(): (local)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (local)")

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

            logger.info(f"upload(): Video successfully saved to {filepath} with caption.")
            return True
        except Exception as e:
            logger.error(f"upload(): Failed to save video locally: {e}")
            return False


class MemoryInstagramSessionManager(BaseInstagramSessionManager):
    def __init__(self):
        """Initialisiert den E-Mail-Speicher im Speicher."""
        logger.info(f"__init__(): (memory)")

    def get_session(self) -> Generator["BaseInstagramSessionManager", None, None]:
        """Erzeugt eine transaktionale Instagram-Sitzung im Speicher."""
        logger.info(f"get_session(): (memory)")
        try:
            yield self
        finally:
            logger.info(f"get_session(): closed session (memory)")

    def upload(self, video_bytes: bytes, video_format: str, caption: str) -> bool:
        """Simuliert das Hochladen eines Videos im Speicher."""
        logger.info(f"upload(): Simulating video upload with caption: {caption}")
        return True


_instagram_session_manager = None

def init_instagram_session_manager():
    global _instagram_session_manager
    logger.info(f"init_instagram_session_manager()")
    
    if _instagram_session_manager is None:
        _instagram_session_manager = LocalInstagramSessionManager() if INSTAGRAM_LOCAL else RemoteInstagramSessionManager()
    else:
        logger.warning(f"init_instagram_session_manager(): already initialized")


def get_instagram_session():
    global _instagram_session_manager
    logger.info(f"get_instagram_session()")
    
    if _instagram_session_manager is None:
        logger.error(f"get_instagram_session(): failed! manager not initialized")
        return

    try:
        gen = _instagram_session_manager.get_session()
        session = next(gen)
        yield session
    except Exception as e:
        logger.error(f"get_instagram_session(): Error: {e}")
        raise e
