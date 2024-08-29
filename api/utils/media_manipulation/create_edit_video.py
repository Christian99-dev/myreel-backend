import os
import tempfile
from api.utils.media_manipulation.resize_for_instagram_reel import resize_for_instagram_reel
from api.utils.media_manipulation.write_videofile_for_instagram_reel import write_videofile_for_instagram_reel
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import numpy as np
import io

def create_edit_video(
    video_bytes: bytes,
    video_format: str,

    audio_bytes: bytes,
    audio_format: str,

    breakpoints: list[float],

    output_video_format: str
) -> bytes:
    """
    Creates a new video by combining segments of an existing video based on breakpoints
    and setting a provided audio track.

    Args:
        video_bytes: Bytes of the input video.
        video_format: Format of the input video (e.g., mp4).
        audio_bytes: Bytes of the audio track.
        audio_format: Format of the audio track (e.g., mp3).
        breakpoints: List of timestamps (in seconds) defining the cuts in the video.
        output_video_format: Format of the output video (e.g., mp4).

    Returns:
        The resulting video as bytes.
    """

    try:
        # Temporarily store video and audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_format}") as video_temp_file:
            video_temp_file.write(video_bytes)
            video_temp_file_path = video_temp_file.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as audio_temp_file:
            audio_temp_file.write(audio_bytes)
            audio_temp_file_path = audio_temp_file.name

        # Load video and audio clips
        video_clip = VideoFileClip(video_temp_file_path)
        audio_clip = AudioFileClip(audio_temp_file_path)

        # Create video segments based on breakpoints
        video_segments = []
        for i in range(1, len(breakpoints)):
            segment_duration = breakpoints[i] - breakpoints[i - 1]
            segment = video_clip.subclip(0, segment_duration)
            video_segments.append(segment)

        # Concatenate video segments
        final_video = concatenate_videoclips(video_segments)

        # Set audio from start of first breakpoint to end of last breakpoint
        audio_start_time = breakpoints[0]
        audio_end_time = breakpoints[-1]
        final_video = final_video.set_audio(audio_clip.subclip(audio_start_time, audio_end_time))

        # final video resize to 9:16
        final_video = resize_for_instagram_reel(final_video)

        # Write final video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_video_format}") as output_temp_file:
            write_videofile_for_instagram_reel(final_video, output_temp_file.name)
            output_file_path = output_temp_file.name

        # Read final video as bytes
        with open(output_file_path, 'rb') as file:
            result_bytes = file.read()

    except Exception as e:
        print(f"An error occurred during video editing: {e}")
        # Consider returning an error code or empty bytes here

    finally:
        # Ensure proper resource management even on errors
        if 'video_clip' in locals():
            video_clip.close()
        if 'audio_clip' in locals():
            audio_clip.close()
        if 'final_video' in locals():
            final_video.close()

        # Delete temporary files
        if os.path.exists(video_temp_file_path):
            os.remove(video_temp_file_path)
        if os.path.exists(audio_temp_file_path):
            os.remove(audio_temp_file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

    # Return the resulting video bytes (or handle errors as needed)
    return result_bytes