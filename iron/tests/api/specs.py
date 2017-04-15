# Define here functions wihch take a model an return it's serialized form
from rest_framework.reverse import reverse

from iron.models import DirectoryEntry


def absolute_reverse(*args, **kwargs):
    return 'http://testserver{}'.format(reverse(*args, **kwargs))


def dir_entry(path):
    entry = DirectoryEntry(path)
    return {
        "path": entry.path,
        "url": absolute_reverse('file-detail', kwargs={'path': entry.path}),
        "kind": entry.kind,
        "size": entry.size,
        "mime_type": entry.mime_type
    }
