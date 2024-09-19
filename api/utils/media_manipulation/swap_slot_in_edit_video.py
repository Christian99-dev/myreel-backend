import logging
import os
import tempfile

from moviepy.editor import VideoFileClip, concatenate_videoclips

from api.exceptions.media_manipulation.media_manipulation import \
    MediaManipulationError
from api.utils.media_manipulation.resize_for_instagram_reel import \
    resize_for_instagram_reel

logger = logging.getLogger("utils.media_manipulation")

def swap_slot_in_edit(
    input_video_bytes: bytes, 
    input_video_start_point: float, 
    input_video_end_point: float,
    input_video_format: str,
    
    new_video_bytes: bytes, 
    new_video_start_point: float, 
    new_video_end_point: float,
    new_video_format: str,
    
    output_video_format: str
) -> bytes:
    logger.info("swap_slot_in_edit(): Start swapping video slots.")
    video_temp_file_path = None
    new_video_temp_file_path = None
    output_file_path = None

    try:
        # Create temporary files for the original and new video
        logger.info("swap_slot_in_edit(): Storing input and new videos in temporary files.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_video_format}") as video_temp_file:
            video_temp_file.write(input_video_bytes)
            video_temp_file_path = video_temp_file.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{new_video_format}") as new_video_temp_file:
            new_video_temp_file.write(new_video_bytes)
            new_video_temp_file_path = new_video_temp_file.name

        # Load the original video and new video
        logger.info("swap_slot_in_edit(): Loading video clips.")
        original_video_clip = VideoFileClip(video_temp_file_path)
        new_video_clip = VideoFileClip(new_video_temp_file_path)

        # Resize the new clip to 9:16
        logger.info("swap_slot_in_edit(): Resizing new video clip.")
        new_video_clip = resize_for_instagram_reel(new_video_clip)

        # Cut parts of the original video
        logger.info("swap_slot_in_edit(): Cutting original video.")
        part1 = original_video_clip.subclip(0, input_video_start_point)
        part3 = original_video_clip.subclip(input_video_end_point)

        # Cut the new video
        logger.info("swap_slot_in_edit(): Cutting new video segment.")
        new_segment = new_video_clip.subclip(new_video_start_point, new_video_end_point)

        # Concatenate the video clips
        logger.info("swap_slot_in_edit(): Concatenating video segments.")
        final_video = concatenate_videoclips([part1, new_segment, part3], method="compose")

        # Transfer the audio stream from the original video
        final_video = final_video.set_audio(original_video_clip.audio)

        # Write the final video to a temporary file
        logger.info("swap_slot_in_edit(): Writing final video to output file.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_video_format}") as output_temp_file:
            final_video.write_videofile(output_temp_file.name, codec='libx264', audio_codec='aac', threads=4, fps=30)
            output_file_path = output_temp_file.name

        # Read the final video as bytes
        with open(output_file_path, 'rb') as file:
            result_bytes = file.read()

    except Exception as e:
        logger.error(f"swap_slot_in_edit(): Error occurred: {e}")
        raise MediaManipulationError(f"An error occurred during slot swapping: {e}")

    finally:
        # Close the video clips and delete temporary files
        logger.info("swap_slot_in_edit(): Cleaning up resources and temporary files.")
        if 'original_video_clip' in locals():
            original_video_clip.close()
        if 'new_video_clip' in locals():
            new_video_clip.close()
        if 'final_video' in locals():
            final_video.close()
        if video_temp_file_path and os.path.exists(video_temp_file_path):
            os.remove(video_temp_file_path)
        if new_video_temp_file_path and os.path.exists(new_video_temp_file_path):
            os.remove(new_video_temp_file_path)
        if output_file_path and os.path.exists(output_file_path):
            os.remove(output_file_path)

    logger.info("swap_slot_in_edit(): Video slot swapping completed successfully.")
    return result_bytes