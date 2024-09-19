import logging

from moviepy.editor import VideoFileClip

from api.exceptions.media_manipulation.media_manipulation import \
    MediaManipulationError

logger = logging.getLogger("utils.media_manipulation")

def resize_for_instagram_reel(clip: VideoFileClip, output_width: int = 1080, output_height: int = 1920) -> VideoFileClip:
    """
    Skaliert und schneidet ein Video zu, sodass es genau dem Format 1080x1920 entspricht.

    Args:
        clip (VideoFileClip): Das Original-Video als MoviePy VideoFileClip.
        output_width (int): Die Zielbreite, standardmäßig 1080.
        output_height (int): Die Zielhöhe, standardmäßig 1920.

    Returns:
        VideoFileClip: Das angepasste Video im 1080x1920 Format.
    """

    logger.info("resize_for_instagram_reel(): Start resizing the video.")
    try:
        original_size = clip.size
        logger.info(f"resize_for_instagram_reel(): Original video size: {original_size}")

        # Calculate the new scale factor
        scale_factor = max(output_width / original_size[0], output_height / original_size[1])
        logger.info(f"resize_for_instagram_reel(): Calculated scale factor: {scale_factor}")

        # Resize the video
        scaled_clip = clip.resize(scale_factor)
        scaled_size = scaled_clip.size
        logger.info(f"resize_for_instagram_reel(): Scaled video size: {scaled_size}")

        # Center the video and crop the excess areas
        x_center = scaled_size[0] / 2
        y_center = scaled_size[1] / 2
        final_clip = scaled_clip.crop(x_center=x_center, y_center=y_center, width=output_width, height=output_height)
        logger.info(f"resize_for_instagram_reel(): Final video size after cropping: {final_clip.size}")

        return final_clip

    except Exception as e:
        logger.error(f"resize_for_instagram_reel(): Error occurred: {e}")
        raise MediaManipulationError(f"An error occurred during resizing: {e}")