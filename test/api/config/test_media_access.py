def test_save(media_access_memory):
    """Test für die save() Methode."""
    media_access_memory.save('test_file.txt', 'test_dir', b'Test content')
    assert 'test_file.txt' in media_access_memory.list('test_dir')
    assert media_access_memory.get('test_file.txt', 'test_dir') == b'Test content'

def test_get(media_access_memory):
    """Test für die get() Methode."""
    media_access_memory.save('test_file.txt', 'test_dir', b'Test content')
    retrieved_content = media_access_memory.get('test_file.txt', 'test_dir')
    assert retrieved_content == b'Test content'
    assert media_access_memory.get('non_existent_file.txt', 'test_dir') is None

def test_list(media_access_memory):
    """Test für die list() Methode."""
    media_access_memory.save('file1.txt', 'test_dir', b'Content 1')
    media_access_memory.save('file2.txt', 'test_dir', b'Content 2')
    files = media_access_memory.list('test_dir')
    assert set(files) == {'file1.txt', 'file2.txt'}

def test_list_all(media_access_memory):
    """Test für die list_all() Methode."""
    media_access_memory.save('file1.txt', 'test_dir1', b'Content 1')
    media_access_memory.save('file2.txt', 'test_dir2', b'Content 2')
    all_files = media_access_memory.list_all()
    assert 'file1.txt' in all_files['test_dir1']
    assert 'file2.txt' in all_files['test_dir2']

def test_delete(media_access_memory):
    """Test für die delete() Methode."""
    media_access_memory.save('test_file.txt', 'test_dir', b'Test content')
    media_access_memory.delete('test_dir', 'test_file.txt')
    assert 'test_file.txt' not in media_access_memory.list('test_dir')

def test_clear(media_access_memory):
    """Test für die clear() Methode."""
    media_access_memory.save('file1.txt', 'test_dir', b'Content 1')
    media_access_memory.save('file2.txt', 'test_dir', b'Content 2')
    media_access_memory.clear()
    assert media_access_memory.list('test_dir') == []