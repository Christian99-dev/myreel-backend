

from api.config.instagram_access import BaseInstagramAccess

def upload(video_bytes: bytes, caption: str, instagram_access: BaseInstagramAccess):
    instagram_access.upload(video_bytes, caption)