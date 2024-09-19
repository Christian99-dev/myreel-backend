from api.exceptions.media_manipulation.media_manipulation import MediaManipulationError
from moviepy.editor import VideoFileClip


def write_videofile_for_instagram_reel(clip: VideoFileClip, output_path: str) -> None:
    """
    Konvertiert und speichert ein Video im MP4-Format gemäß den Instagram-Spezifikationen.

    Args:
        clip (VideoFileClip): Das Original-Video.
        output_path (str): Der Pfad, an dem das konvertierte Video gespeichert wird.
    """
    # Setze die ffmpeg-Parameter entsprechend den Instagram-Spezifikationen
    try:
        ffmpeg_params = [
            "-aspect", "9:16",
            "-framerate", "1/60",
            "-r", "25",
            "-c:v", "h264",
            "-tune", "stillimage",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ac", "2",
            "-ar", "44100",
            "-pix_fmt", "yuv420p",
            "-max_muxing_queue_size", "1024",
            "-shortest"
        ]

        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            ffmpeg_params=ffmpeg_params
        )

    except Exception as e:
        raise MediaManipulationError(f"An error occurred while writing the video file: {e}")