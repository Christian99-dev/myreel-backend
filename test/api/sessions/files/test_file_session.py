import logging
logger = logging.getLogger("test.unittest")

def test_save(memory_file_session):
    """Test für die save() Methode."""
    memory_file_session.save('test_file.txt', 'test_dir', b'Test content')
    assert 'test_file.txt' in memory_file_session.list('test_dir')
    assert memory_file_session.get('test_file.txt', 'test_dir') == b'Test content'

def test_get(memory_file_session):
    """Test für die get() Methode."""
    memory_file_session.save('test_file.txt', 'test_dir', b'Test content')
    retrieved_content = memory_file_session.get('test_file.txt', 'test_dir')
    assert retrieved_content == b'Test content'
    assert memory_file_session.get('non_existent_file.txt', 'test_dir') is None

def test_list(memory_file_session):
    """Test für die list() Methode."""
    memory_file_session.save('file1.txt', 'test_dir', b'Content 1')
    memory_file_session.save('file2.txt', 'test_dir', b'Content 2')
    files = memory_file_session.list('test_dir')
    assert set(files) == {'file1.txt', 'file2.txt'}

def test_list_all(memory_file_session):
    """Test für die list_all() Methode."""
    memory_file_session.save('file1.txt', 'test_dir1', b'Content 1')
    memory_file_session.save('file2.txt', 'test_dir2', b'Content 2')
    all_files = memory_file_session.list_all()

    assert 'test_dir1/file1.txt' in all_files
    assert 'test_dir2/file2.txt' in all_files

def test_delete(memory_file_session):
    """Test für die delete() Methode."""
    memory_file_session.save('test_file.txt', 'test_dir', b'Test content')
    memory_file_session.delete('test_dir', 'test_file.txt')
    assert 'test_file.txt' not in memory_file_session.list('test_dir')

def test_clear(memory_file_session):
    """Test für die clear() Methode."""
    memory_file_session.save('file1.txt', 'test_dir', b'Content 1')
    memory_file_session.save('file2.txt', 'test_dir', b'Content 2')
    memory_file_session.clear()
    assert memory_file_session.list('test_dir') == []