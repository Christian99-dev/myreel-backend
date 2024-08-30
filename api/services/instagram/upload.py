

from api.config.instagram_access import BaseInstagramAccess

def upload(video_bytes: bytes, video_format:str, caption: str, instagram_access: BaseInstagramAccess):
    return instagram_access.upload(video_bytes, video_format, caption)