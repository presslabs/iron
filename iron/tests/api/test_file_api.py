from io import BytesIO

from iron.tests.api import specs


def test_list_root(default_root, api_client):
    default_root.mkdir('test-dir')
    default_root.join('test-file').write('')

    response = api_client.get('/files/')
    assert response.status_code == 200
    assert [specs.dir_entry('test-dir'),
            specs.dir_entry('test-file')] == response.data


def test_list_subdir(default_root, api_client):
    default_root.mkdir('test-dir')
    default_root.join('test-dir').mkdir('test-subdir')
    default_root.join('test-dir').join('test-file').write('')

    response = api_client.get('/files/test-dir/')
    assert response.status_code == 200
    assert [specs.dir_entry('test-dir/test-file'),
            specs.dir_entry('test-dir/test-subdir')] == response.data


def test_get_dir_without_trailing_slash_returns_404(default_root, api_client):
    default_root.mkdir('test-dir')

    response = api_client.get('/files/test-dir/')
    assert response.status_code == 200, response.data

    response = api_client.get('/files/test-dir')
    assert response.status_code == 404, response.data


def test_mkdir(default_root, api_client):
    response = api_client.post('/files', {'path': 'test-dir',
                                          'kind': 'directory'})
    assert response.status_code == 201, response.data
    entry = specs.dir_entry('test-dir')
    assert 'location' in response
    assert response['location'] == entry['url']
    assert response.data == entry
    assert default_root.join('test-dir').check(dir=True)


def test_create_file(default_root, api_client):
    response = api_client.post('/files', {'path': 'test-file',
                                          'content': BytesIO(b'test-content'),
                                          'kind': 'file'},
                               format='multipart')

    assert response.status_code == 201, response.data
    entry = specs.dir_entry('test-file')
    assert 'location' in response
    assert response['location'] == entry['url']
    assert response.data == entry
    assert default_root.join('test-file').check()
    assert default_root.join('test-file').read('rb') == b'test-content'


def test_rename_file(default_root, api_client):
    default_root.join('test-file').write(b'test-content')

    response = api_client.patch('/files/test-file', {'path': 'renamed-file'})
    assert response.status_code == 303, response.data
    assert default_root.join('test-file').check() is False

    renamed_entry = specs.dir_entry('renamed-file')
    assert 'location' in response
    assert response['location'] == renamed_entry['url']
    assert response.data == renamed_entry
    assert default_root.join('renamed-file').check()
    assert default_root.join('renamed-file').read('rb') == b'test-content'


def test_rename_file_with_trailing_slash(default_root, api_client):
    default_root.join('test-file').write(b'test-content')

    response = api_client.patch('/files/test-file/', {'path': 'renamed-file'})
    assert response.status_code == 404, response.data


def test_rename_dir(default_root, api_client):
    default_root.mkdir('test-dir')

    response = api_client.patch('/files/test-dir', {'path': 'renamed-dir'})
    assert response.status_code == 303, response.data
    assert default_root.join('test-dir').check() is False

    renamed_entry = specs.dir_entry('renamed-dir')
    assert 'location' in response
    assert response['location'] == renamed_entry['url']
    assert response.data == renamed_entry
    assert default_root.join('renamed-dir').check(dir=True)


def test_update_file_content(default_root, api_client):
    default_root.join('test-file').write(b'test-content')

    response = api_client.put('/files/test-file', {'path': 'test-file',
                                                   'content': BytesIO(b'updated-content'),
                                                   'kind': 'file'},
                              format='multipart')

    entry = specs.dir_entry('test-file')

    assert response.status_code == 200, response.data
    assert response.data == entry
    assert default_root.join('test-file').check()
    assert default_root.join('test-file').read('rb') == b'updated-content'


def test_put_fails_on_directories(default_root, api_client):
    default_root.mkdir('test-dir')

    response = api_client.put('/files/test-dir', {'path': 'test-dir',
                                                  'content': '',
                                                  'kind': 'file'},
                              format='multipart')

    assert response.status_code == 405, response.data


def test_remove_file(default_root, api_client):
    default_root.join('test-file').write('')

    response = api_client.delete('/files/inexistent-test-file')
    assert response.status_code == 404, response.data

    response = api_client.delete('/files/test-file')
    assert response.status_code == 204, response.data
    assert default_root.join('test-file').check() is False


def test_remove_dir(default_root, api_client):
    default_root.mkdir('test-dir')

    response = api_client.delete('/files/inexistent-test-dir')
    assert response.status_code == 404, response.data

    response = api_client.delete('/files/test-dir')
    assert response.status_code == 204, response.data
    assert default_root.join('test-dir').check() is False


def test_recursive_remove_dir(default_root, api_client):
    default_root.mkdir('test-dir').join('test-file').write('')

    response = api_client.delete('/files/test-dir?recursive=true')
    assert response.status_code == 204, response.data
    assert default_root.join('test-dir').check() is False
