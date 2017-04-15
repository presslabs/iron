import os
import shutil
import stat
import mimetypes

from django.conf import settings
from pl_sugar.utils import memoized_property


class DirectoryEntry:
    class Kinds:
        DIRECTORY = 'directory'
        FILE = 'file'

        @classmethod
        def as_list(cls):
            return [cls.DIRECTORY,
                    cls.FILE]

        @classmethod
        def as_choices(cls):
            return [(kind, kind) for kind in DirectoryEntry.Kinds.as_list()]

    def __init__(self, path):
        self._set_path(path)

    def _set_path(self, path):
        self.path = path
        self.kind = DirectoryEntry.Kinds.FILE
        if stat.S_ISDIR(self.stat.st_mode):
            self.kind = DirectoryEntry.Kinds.DIRECTORY
            self.path += '/'

    def _clear_memoized_properties(self):
        attrs = [attr for attr in self.__dict__.keys() if attr.startswith('__cached_')]
        for attr in attrs:
            delattr(self, attr)

    def rename(self, path):
        renamed_full_path = os.path.join(settings.IRON_ROOT, path)
        os.rename(self.full_path, renamed_full_path)
        self._clear_memoized_properties()
        self._set_path(path)

    def update_content(self, content):
        with open(self.full_path, 'wb') as f:
            for chunk in content.chunks(4096):
                f.write(chunk)

    @memoized_property
    def stat(self):
        return os.lstat(self.full_path)

    @property
    def size(self):
        return self.stat.st_size

    @memoized_property
    def mime_type(self):
        mime_type = mimetypes.guess_type(self.path)[0]
        if mime_type is None:
            if self.kind == DirectoryEntry.Kinds.DIRECTORY:
                mime_type = 'application/x-directory'
            else:
                mime_type = 'application/octet-stream'
        else:
            if not mime_type.startswith(('image/', 'text/')):
                mime_type = 'application/octet-stream'
        return mime_type

    @memoized_property
    def full_path(self):
        return os.path.join(settings.IRON_ROOT, self.path)

    @classmethod
    def ls(cls, path):
        full_path = os.path.join(settings.IRON_ROOT, path)
        for item in sorted(os.listdir(full_path)):
            yield cls(os.path.join(path, item))

    @classmethod
    def mkdir(cls, path):
        full_path = os.path.join(settings.IRON_ROOT, path)
        os.mkdir(full_path)
        return cls(path)

    @classmethod
    def create_file(cls, path, content):
        full_path = os.path.join(settings.IRON_ROOT, path)
        with open(full_path, 'wb') as f:
            for chunk in content.chunks(4096):
                f.write(chunk)
        return cls(path)

    @classmethod
    def remove(cls, path, recursive=False):
        entry = cls(path)
        if entry.kind == cls.Kinds.DIRECTORY:
            if recursive:
                shutil.rmtree(entry.full_path)
            else:
                os.rmdir(entry.full_path)
        else:
            os.unlink(entry.full_path)
