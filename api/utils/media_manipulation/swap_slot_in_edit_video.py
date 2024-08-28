import os
import tempfile
from typing import List
from moviepy.editor import VideoFileClip, concatenate_videoclips

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
    video_temp_file_path = None
    new_video_temp_file_path = None
    output_file_path = None

    try:
        # Temporäre Dateien für das ursprüngliche Video und das neue Video erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_video_format}") as video_temp_file:
            video_temp_file.write(input_video_bytes)
            video_temp_file_path = video_temp_file.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{new_video_format}") as new_video_temp_file:
            new_video_temp_file.write(new_video_bytes)
            new_video_temp_file_path = new_video_temp_file.name
        
        # Lade das ursprüngliche Video und das neue Video von den temporären Dateien
        original_video_clip = VideoFileClip(video_temp_file_path, target_resolution=(1080, 1920))
        new_video_clip = VideoFileClip(new_video_temp_file_path, target_resolution=(1080, 1920))
        
        # Schneide die Teile des ursprünglichen Videos
        part1 = original_video_clip.subclip(0, input_video_start_point)  # Von 0 bis video_start_point
        part3 = original_video_clip.subclip(input_video_end_point)       # Von video_end_point bis zum Ende
        
        # Schneide das neue Video
        new_segment = new_video_clip.subclip(new_video_start_point, new_video_end_point)

        # Kombiniere die Video-Clips
        final_video = concatenate_videoclips([part1, new_segment, part3], method="chain")
        
        # Übertrage die Audiostreams aus dem Originalvideo
        final_video = final_video.set_audio(original_video_clip.audio)
        
        # Schreibe das finale Video in eine temporäre Datei
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_video_format}") as output_temp_file:
            final_video.write_videofile(output_temp_file.name, codec='libx264', audio_codec='aac', threads=4, fps=24)
            output_file_path = output_temp_file.name

        # Lies die fertige Datei in ein Bytes-Objekt
        with open(output_file_path, 'rb') as file:
            result_bytes = file.read()
    
    finally:
        # Schließe die Video- und Audiodateien und lösche die temporären Dateien
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
    
    # Gib das resultierende Video als Bytes zurück
    return result_bytes