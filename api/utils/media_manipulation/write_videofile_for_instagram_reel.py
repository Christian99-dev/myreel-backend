import logging

from moviepy.editor import VideoFileClip

from api.exceptions.media_manipulation.media_manipulation import \
    MediaManipulationError

logger = logging.getLogger("utils.media_manipulation")

def write_videofile_for_instagram_reel(clip: VideoFileClip, output_path: str) -> None:
    """
    Konvertiert und speichert ein Video im MP4-Format gemäß den Instagram-Spezifikationen.

    Args:
        clip (VideoFileClip): Das Original-Video.
        output_path (str): Der Pfad, an dem das konvertierte Video gespeichert wird.
    """
    logger.info(f"write_videofile_for_instagram_reel(): Start writing video to {output_path}.")
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
        logger.info(f"write_videofile_for_instagram_reel(): Video successfully written to {output_path}.")

    except Exception as e:
        logger.error(f"write_videofile_for_instagram_reel(): Error occurred: {e}")
        raise MediaManipulationError(f"An error occurred while writing the video file: {e}")