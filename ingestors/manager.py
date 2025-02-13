import magic
import logging
from timeit import default_timer
from tempfile import mkdtemp
from datetime import datetime
from banal import ensure_list
from followthemoney import model
from normality import stringify
from pantomime import normalize_mimetype
from servicelayer.archive import init_archive
from servicelayer.archive.util import ensure_path
from ftmstore.utils import safe_fragment


from ingestors.exc import ProcessingException, ENCRYPTED_MSG
from ingestors.util import filter_text, remove_directory
from ingestors import settings
from ingestors.pdf import PDFIngestor
from ingestors.image import ImageIngestor
from ingestors.djvu import DjVuIngestor
from ingestors.tiff import TIFFIngestor
from ingestors.office import DocumentIngestor
from ingestors.opendoc import OpenDocumentIngestor
from ingestors.ooxml import OfficeOpenXMLIngestor

log = logging.getLogger(__name__)


class Manager(object):
    """Handles the lifecycle of an ingestor. This can be subclassed to embed it
    into a larger processing framework."""

    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = "success"
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = "failure"

    MAGIC = magic.Magic(mime=True)

    def __init__(self):
        self.work_path = ensure_path(mkdtemp(prefix="ingestor-"))
        self.emitted = set()
        self.context = {}
        self.ingestor_classes = [
            PDFIngestor, ImageIngestor, DjVuIngestor, TIFFIngestor, DocumentIngestor,
            OpenDocumentIngestor, OfficeOpenXMLIngestor
        ]

    @property
    def archive(self):
        if not hasattr(settings, "_archive"):
            settings._archive = init_archive()
        return settings._archive

    def make_entity(self, schema, parent=None):
        schema = model.get(schema)
        entity = model.make_entity(schema)
        self.make_child(parent, entity)
        return entity

    def make_child(self, parent, child):
        """Derive entity properties by knowing it's parent folder."""
        if parent is not None and child is not None:
            # Folder hierarchy:
            child.add("parent", parent.id)
            child.add("ancestors", parent.get("ancestors"))
            child.add("ancestors", parent.id)

    def emit_entity(self, entity, fragment=None):
        self.emitted.add(entity.id)

    def emit_text_fragment(self, entity, texts, fragment):
        texts = [t for t in ensure_list(texts) if filter_text(t)]
        if len(texts):
            doc = self.make_entity(entity.schema)
            doc.id = entity.id
            doc.add("indexText", texts)
            self.emit_entity(doc, fragment=safe_fragment(fragment))

    def auction(self, file_path, entity):
        if not entity.has("mimeType"):
            entity.add("mimeType", self.MAGIC.from_file(file_path.as_posix()))

        if "application/encrypted" in entity.get("mimeType"):
            raise ProcessingException(ENCRYPTED_MSG)

        best_score, best_cls = 0, None
        for cls in self.ingestor_classes:
            score = cls.match(file_path, entity)
            if score > best_score:
                best_score = score
                best_cls = cls

        import pdb;pdb.set_trace()
        if best_cls is None:
            raise ProcessingException("Format not supported")
        return best_cls

    def store(self, file_path, mime_type=None):
        file_path = ensure_path(file_path)
        mime_type = normalize_mimetype(mime_type)
        if file_path is not None and file_path.is_file():
            return self.archive.archive_file(file_path, mime_type=mime_type)

    def load(self, content_hash, file_name=None):
        # log.info("Local archive name: %s", file_name)
        return self.archive.load_file(
            content_hash, file_name=file_name, temp_path=self.work_path
        )

    def ingest(self, file_path, entity, **kwargs):
        """Main execution step of an ingestor."""
        file_path = ensure_path(file_path)
        file_size = None

        if file_path.is_file():
            file_size = file_path.stat().st_size  # size in bytes

        if file_size is not None and not entity.has("fileSize"):
            entity.add("fileSize", file_size)

        now = datetime.now()
        now_string = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

        entity.set("processingStatus", self.STATUS_FAILURE)
        entity.set("processedAt", now_string)

        ingestor_class = None
        ingestor_name = None

        try:
            ingestor_class = self.auction(file_path, entity)
            ingestor_name = ingestor_class.__name__
            log.info(f"Ingestor [{repr(entity)}]: {ingestor_name}")

            start_time = default_timer()
            self.delegate(ingestor_class, file_path, entity)
            duration = max(0, default_timer() - start_time)

            entity.set("processingStatus", self.STATUS_SUCCESS)
        except ProcessingException as pexc:
            log.exception(f"[{repr(entity)}] Failed to process: {pexc}")
            entity.set("processingError", stringify(pexc))
        finally:
            self.finalize(entity)

    def finalize(self, entity):
        self.emit_entity(entity)
        remove_directory(self.work_path)

    def delegate(self, ingestor_class, file_path, entity):
        ingestor_class(self).ingest(file_path, entity)

    def close(self):
        remove_directory(self.work_path)
