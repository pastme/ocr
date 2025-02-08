from uuid import uuid4
from servicelayer.archive.util import ensure_path

from ingestors.exc import ProcessingException
from servicelayer.archive.util import ensure_path

from tempfile import mkdtemp


work_path = ensure_path(mkdtemp(prefix="ingestor-"))

class TempFileSupport(object):
    """Provides helpers for file system related tasks."""

    def make_empty_directory(self):
        directory_path = work_path.joinpath(uuid4().hex)
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def make_work_file(self, file_name, prefix=None):
        if prefix is not None:
            prefix = ensure_path(prefix)
            if work_path not in prefix.parents:
                raise ProcessingException("Path escalation: %r" % prefix)
        prefix = prefix or work_path
        work_file = prefix.joinpath(file_name)
        work_file = work_file.resolve()
        if prefix not in work_file.parents:
            raise ProcessingException("Path escalation: %r" % file_name)
        if not work_file.parent.exists():
            work_file.parent.mkdir(parents=True, exist_ok=True)
        return work_file
