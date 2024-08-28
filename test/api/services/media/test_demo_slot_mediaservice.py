from api.services.media.demo_slot import get

def test_get_demo_slot_video(media_access_memory):
    # Ruft die get-Funktion auf
    result = get(media_access_memory)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result is not None