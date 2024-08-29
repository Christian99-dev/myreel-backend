from moviepy.editor import VideoFileClip


def write_videofile_for_instagram_reel(clip: VideoFileClip, output_path: str) -> None:
        """
        Konvertiert und speichert ein Video im MP4-Format gemäß den Instagram-Spezifikationen.

        Args:
            clip (VideoFileClip): Das Original-Video.
            output_path (str): Der Pfad, an dem das konvertierte Video gespeichert wird.
        """
        # Setze die ffmpeg-Parameter entsprechend den Instagram-Spezifikationen
        # Setze die ffmpeg-Parameter entsprechend den Instagram-Spezifikationen
        ffmpeg_params = [
            "-aspect", "9:16",                # Seitenverhältnis auf 9:16 setzen
            "-framerate", "1/60",             # Setzt die Framerate auf 1 Bild pro 60 Sekunden
            "-r", "25",                       # Setzt die Ausgabe-Framerate auf 25 FPS
            "-c:v", "h264",                   # Video Codec auf h264 setzen
            "-tune", "stillimage",            # Tunen für Standbilder
            "-crf", "18",                     # CRF-Wert auf 18 setzen für hohe Qualität
            "-c:a", "aac",                    # Audio Codec auf AAC setzen
            "-b:a", "128k",                   # Audio-Bitrate auf 128 kbps setzen
            "-ac", "2",                       # Anzahl der Audiokanäle auf 2 setzen (Stereo)
            "-ar", "44100",                   # Audio-Abtastrate auf 44100 Hz setzen
            "-pix_fmt", "yuv420p",            # Pixel-Format auf yuv420p setzen
            "-max_muxing_queue_size", "1024", # Maximaler Multiplexing-Warteschlangenwert
            "-shortest"                       # Beendet das Video, wenn die kürzeste Eingangsdatei endet
        ]

        # Speichere das Video mit den ffmpeg-Parametern
        clip.write_videofile(
            output_path,
            codec='libx264',                  # Video-Codec
            audio_codec='aac',                # Audio-Codec
            ffmpeg_params=ffmpeg_params
        )