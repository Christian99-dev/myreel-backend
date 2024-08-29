from moviepy.editor import VideoFileClip

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
    # Ursprüngliche Video-Größe
    original_size = clip.size
    print("Original Video Size:", original_size)  # Zeigt die ursprüngliche Größe des Videos an

    # Berechne den neuen Skalierungsfaktor
    scale_factor = max(output_width / original_size[0], output_height / original_size[1])
    print("Calculated Scale Factor:", scale_factor)  # Zeigt den berechneten Skalierungsfaktor an

    # Skaliere das Video
    scaled_clip = clip.resize(scale_factor)
    scaled_size = scaled_clip.size
    print("Scaled Video Size:", scaled_size)  # Zeigt die Größe nach der Skalierung an

    # Zentriere das Video und schneide die überstehenden Bereiche ab
    x_center = scaled_size[0] / 2
    y_center = scaled_size[1] / 2
    print("Center Coordinates (x, y):", (x_center, y_center))  # Zeigt die Mittelpunktkoordinaten an

    final_clip = scaled_clip.crop(x_center=x_center,
                                   y_center=y_center,
                                   width=output_width,
                                   height=output_height)

    final_size = final_clip.size
    print("Final Video Size:", final_size)  # Zeigt die endgültige Größe des Videos an
    return final_clip