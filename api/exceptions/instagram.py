class InstagramUploadError(Exception):
    """Exception raised when there is an error during Instagram upload."""
    pass

class FTPConnectionError(Exception):
    """Exception raised when there is an error connecting to the FTP server."""
    pass

class FTPUploadError(Exception):
    """Exception raised when there is an error uploading the video to the FTP server."""
    pass

class MediaContainerCreationError(Exception):
    """Exception raised when there is an error creating the media container on Instagram."""
    pass

class VideoPublishError(Exception):
    """Exception raised when there is an error publishing the video on Instagram."""
    pass