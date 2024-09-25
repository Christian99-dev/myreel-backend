import os
import tempfile

from fastapi import UploadFile
from moviepy.editor import AudioFileClip


def get_audio_duration(file_bytes: bytes, file_format: str) -> float:
    # Erstelle eine temporäre Datei mit dem Dateiinhalt
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}') as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        # Lade die Audiodatei mit moviepy
        audio_clip = AudioFileClip(temp_file_path)

        # Erhalte die Dauer der Audiodatei
        duration = audio_clip.duration

        # Schließe den Audio-Clip
        audio_clip.close()
    except Exception as e:
        # Behandle die Ausnahme (z.B. loggen, erneut werfen, etc.)
        raise e
    finally:
        # Stelle sicher, dass die temporäre Datei gelöscht wird
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return duration