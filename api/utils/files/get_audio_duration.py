import os
import tempfile
from fastapi import UploadFile
from moviepy.editor import AudioFileClip

def get_audio_duration(file: UploadFile, file_format: str) -> float:
    # Create a temporary file to save the uploaded audio content
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}') as temp_file:
        temp_file.write(file.file.read())
        temp_file_path = temp_file.name

    try:
        # Load the audio file using moviepy
        audio_clip = AudioFileClip(temp_file_path)

        # Get the duration of the audio file
        duration = audio_clip.duration

        # Close the audio clip
        audio_clip.close()
    except Exception as e:
        # Handle the exception (e.g., log it, re-raise it, etc.)
        raise e
    finally:
        # Ensure the temporary file is deleted
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return duration