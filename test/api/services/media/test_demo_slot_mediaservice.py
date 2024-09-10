from api.services.files.demo_slot import get

def test_get_demo_slot_video(memory_file_session):
    # Ruft die get-Funktion auf
    result = get(memory_file_session)

    # Überprüfe, ob die zurückgegebenen Daten korrekt sind
    assert result is not None