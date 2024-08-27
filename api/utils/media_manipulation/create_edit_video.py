import os
import tempfile
from typing import List
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import numpy as np
import io

def create_edit_video(video_bytes: bytes, audio_bytes: bytes, breakpoints: list[float], video_format: str, audio_format: str, output_video_format: str) -> bytes:
    # Temporäre Dateien für Video und Audio erstellen
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_format}") as video_temp_file:
        video_temp_file.write(video_bytes)
        video_temp_file_path = video_temp_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as audio_temp_file:
        audio_temp_file.write(audio_bytes)
        audio_temp_file_path = audio_temp_file.name
    
    # Lade das Video und Audio von den temporären Dateien
    video_clip = VideoFileClip(video_temp_file_path)
    audio_clip = AudioFileClip(audio_temp_file_path)
    
    # Liste zur Speicherung der Videosegmente erstellen
    video_segments = []
    
    # Segmente basierend auf den Breakpoints erstellen
    for i in range(1, len(breakpoints)):
        segment_duration = breakpoints[i] - breakpoints[i - 1]
        segment = video_clip.subclip(0, segment_duration)
        video_segments.append(segment)
    
    # Alle Videosegmente zusammenfügen
    final_video = concatenate_videoclips(video_segments)
    
    # Setze das Audio, beginnend ab dem ersten Breakpoint bis zum letzten
    audio_start_time = breakpoints[0]
    audio_end_time = breakpoints[-1]
    final_video = final_video.set_audio(audio_clip.subclip(audio_start_time, audio_end_time))
    
    # Schreibe das finale Video in eine temporäre Datei
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_video_format}") as output_temp_file:
        final_video.write_videofile(output_temp_file.name, codec='libx264', audio_codec='aac', threads=4, fps=24)
        output_file_path = output_temp_file.name
    
    # Lies die fertige Datei in ein Bytes-Objekt
    with open(output_file_path, 'rb') as file:
        result_bytes = file.read()
    
    # Schließe die Video- und Audiodateien und lösche die temporären Dateien
    video_clip.close()
    audio_clip.close()
    final_video.close()
    os.remove(video_temp_file_path)
    os.remove(audio_temp_file_path)
    os.remove(output_file_path)
    
    # Gib das resultierende Video als Bytes zurück
    return result_bytes