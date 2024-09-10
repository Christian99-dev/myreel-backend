from api.sessions.instagram import BaseInstagramSessionManager

def upload(video_bytes: bytes, video_format:str, caption: str, instagram_access: BaseInstagramSessionManager):
    return instagram_access.upload(video_bytes, video_format, caption)