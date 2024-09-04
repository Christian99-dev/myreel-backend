file_config = {
    "video": {
        "formats": ["video/mp4", "video/x-msvideo", "video/x-matroska"],  # z.B. MP4, AVI, MKV
        "max_size": 100 * 1024 * 1024  # 5 MB in Bytes
    },
    "image": {
        "formats": ["image/jpeg", "image/png", "image/gif"],  # z.B. JPEG, PNG, GIF
        "max_size": 100 * 1024 * 1024  # 2 MB in Bytes
    },
    "audio": {
        "formats": ["audio/mpeg", "audio/wav"],  # z.B. MP3, WAV
        "max_size": 100 * 1024 * 1024  # 10 MB in Bytes
    }
}