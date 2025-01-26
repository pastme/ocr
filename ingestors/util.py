import shutil
import locale
from pathlib import Path
from contextlib import contextmanager


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


def remove_directory(file_path):
    """Delete a directory, ignore errors."""
    try:
        shutil.rmtree(file_path, True)
    except Exception:
        pass

def path_string(path):
    """Convert possible path objects to strings."""
    if isinstance(path, Path):
        return path.as_posix()
    return path


@contextmanager
def temp_locale(temp):
    try:
        currlocale = locale.getlocale()
    except ValueError:
        currlocale = ("en_US", "UTF-8")
    locale.setlocale(locale.LC_CTYPE, temp)
    yield
    locale.setlocale(locale.LC_CTYPE, currlocale)
